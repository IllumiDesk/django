import logging
from datetime import datetime
from django.db import models, transaction
from django.conf import settings
from django.utils import timezone

from billing.models import (Customer, Invoice,
                            Plan, Subscription,
                            Card, Event)
log = logging.getLogger('billing')

if settings.MOCK_STRIPE:
    from billing.tests import mock_stripe as stripe
    log.info("Importing mock stripe in stripe utils.")
else:
    import stripe


stripe.api_key = settings.STRIPE_SECRET_KEY


def handle_foreign_key_field(stripe_data, stripe_field, model_field):
    init_value = stripe_data[stripe_field]
    final_value = None
    identifier = None

    if init_value is not None:
        if isinstance(init_value, dict):
            identifier = init_value.get("id")

        elif isinstance(init_value, model_field.related_model):
            final_value = init_value

        else:
            identifier = init_value

        if hasattr(model_field.related_model, "stripe_id"):
            kwargs = {'stripe_id': identifier}
        elif final_value is None:
            kwargs = {'pk': identifier}

        if final_value is None:
            final_value = model_field.related_model.objects.filter(**kwargs).first()

    return final_value


def convert_field_to_stripe(model, stripe_field, stripe_data):
    field_name = "stripe_id" if stripe_field == "id" else stripe_field
    value = stripe_data[stripe_field]

    all_model_field_names = [f.name for f in model._meta.get_fields()]
    if field_name in all_model_field_names:  # or field_name.replace("_id", "") in all_model_field_names:
        model_field = model._meta.get_field(field_name)
    else:
        model_field = field_name = value = None

    # Not sure how to handle many to many fields just yet. Not sure we will have to.
    # I've really come to hate this following block.
    # Will have to think about how to clean it up.
    # I'm guessing it's also not very performant
    if (model_field is not None and
        (model_field.is_relation and not model_field.many_to_many)):

        value = handle_foreign_key_field(stripe_data,
                                         stripe_field,
                                         model_field)

    elif isinstance(model_field, models.DateTimeField):
        if value is not None:
            value = datetime.fromtimestamp(value)
            value = timezone.make_aware(value)

    return (field_name, value)


def convert_stripe_object(model, stripe_obj):
    dict_tuples = [convert_field_to_stripe(model, field, stripe_obj)
                   for field in stripe_obj]
    converted = dict(tup for tup in dict_tuples if tup[0] is not None)
    if "created" not in converted:
        converted['created'] = timezone.make_aware(datetime.now())
    return converted


def create_stripe_customer_from_user(auth_user):
    stripe_response = stripe.Customer.create(description=auth_user.first_name + " " + auth_user.last_name,
                                             email=auth_user.email)

    # Meh.
    stripe_response['user'] = auth_user.pk

    converted_data = convert_stripe_object(Customer, stripe_response)
    return Customer.objects.create(**converted_data)


def create_plan_in_stripe(validated_data):
    stripe_response = stripe.Plan.create(id=validated_data.get('name').lower().replace(" ", "-"),
                                         amount=validated_data.get('amount'),
                                         currency=validated_data.get('currency'),
                                         interval=validated_data.get('interval'),
                                         interval_count=validated_data.get('interval_count'),
                                         name=validated_data.get('name'),
                                         statement_descriptor=validated_data.get('statement_descriptor'),
                                         trial_period_days=validated_data.get('trial_period_days'))

    converted_data = convert_stripe_object(Plan, stripe_response)
    return Plan.objects.create(**converted_data)


def create_subscription_in_stripe(validated_data, user=None):
    customer = validated_data.get("customer")
    if customer is None and user is None:
        raise ValueError("Validated_data must contain 'user', or the user object"
                         "must be passed as a kwarg.")
    if customer is None:
        customer = user.customer

    plan_id = validated_data.get("plan")

    if isinstance(plan_id, Plan):
        plan = plan_id
    else:
        plan = Plan.objects.get(pk=plan_id)

    stripe_response = stripe.Subscription.create(customer=customer.stripe_id,
                                                 plan=plan.stripe_id)
    converted_data = convert_stripe_object(Subscription, stripe_response)
    return Subscription.objects.create(**converted_data)


def create_card_in_stripe(validated_data, user=None):
    user_pk = validated_data.get("user")
    if user is None and user_pk is None:
        raise ValueError("Validated_data must contain 'user', or the user object"
                         " must be passed as a kwarg.")
    if user is None:
        customer = Customer.objects.get(user__pk=user_pk)
    else:
        customer = user.customer

    stripe_cust = stripe.Customer.retrieve(customer.stripe_id)

    token = validated_data.get("token")
    if token is None:
        validated_data['object'] = "card"
        stripe_resp = stripe_cust.sources.create(source=validated_data)
    else:
        stripe_resp = stripe_cust.sources.create(source=token)

    stripe_resp['customer'] = customer.stripe_id

    converted_data = convert_stripe_object(Card, stripe_resp)
    return Card.objects.create(**converted_data)


def sync_invoices_for_customer(customer, stripe_invoices=None):
    if stripe_invoices is None:
        stripe_invoices = stripe.Invoice.list(customer=customer.stripe_id)

    for stp_invoice in stripe_invoices:
        stp_invoice['invoice_date'] = stp_invoice['date']
        converted_data = convert_stripe_object(Invoice, stp_invoice)
        tbs_invoice = Invoice.objects.filter(stripe_id=converted_data['stripe_id']).first()
        if tbs_invoice is not None:
            for key in converted_data:
                setattr(tbs_invoice, key, converted_data[key])
        else:
            tbs_invoice = Invoice(**converted_data)

        tbs_invoice.save()

    customer.last_invoice_sync = timezone.make_aware(datetime.now())
    customer.save()


def handle_stripe_invoice_webhook(stripe_obj):
    """
    :param stripe_obj: The Stripe *event* object
    :return: None
    """
    event = Event.objects.filter(stripe_id=stripe_obj['id'])
    if not event.exists():
        # This conversion is *just* custom enough that using the convert method isn't useful
        create_ts = datetime.fromtimestamp(stripe_obj['created'])
        create_ts = timezone.make_aware(create_ts)
        event_parms = {'stripe_id': stripe_obj['id'],
                       'created': create_ts,
                       'livemode': stripe_obj['livemode'],
                       'api_version': stripe_obj['api_version'],
                       'event_type': stripe_obj['type']}
        event = Event(**event_parms)
        event.save()
        log.info("Created new stripe event: {event}:{type}".format(event=event.stripe_id,
                                                                   type=event.event_type))
        if event.event_type == "invoice.payment_failed":
            # Suspend the subscription...
            sub_stripe_id = stripe_obj['data']['object']['subscription']
            stripe_subscription = stripe.Subscription.retrieve(sub_stripe_id)
            converted_data = convert_stripe_object(Subscription, stripe_subscription)
            subscription = Subscription.objects.get(stripe_id=sub_stripe_id)
            for key in converted_data:
                if key not in ["customer", "plan"]:
                    setattr(subscription, key, converted_data[key])
            subscription.save()
            log.debug("Updated subscription {sub} after payment failure.".format(sub=subscription.stripe_id))

        stripe_invoice = stripe_obj['data']['object']
        stripe_invoice['invoice_date'] = stripe_invoice['date']
        converted = convert_stripe_object(Invoice, stripe_invoice)
        invoice, created = Invoice.objects.update_or_create(stripe_id=converted['stripe_id'],
                                                            defaults=converted)
        if created:
            log.info("Created a new invoice: {invoice}".format(invoice=invoice.pk))
        else:
            log.info("Updated an invoice: {invoice}".format(invoice=invoice.stripe_id))
    else:
        log.info("Event {event}:{type} already exists. Doing nothing.".format(event=stripe_obj['id'],
                                                                              type=stripe_obj['type']))
