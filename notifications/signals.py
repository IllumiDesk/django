import logging
from django.dispatch import receiver
from billing.models import Subscription
from billing.signals import (subscription_cancelled,
                             subscription_created,
                             invoice_payment_success,
                             invoice_payment_failure)
from .models import Notification, NotificationType
log = logging.getLogger('notifications')


@receiver(subscription_cancelled, sender=Subscription)
def sub_cancelled_handler(sender, **kwargs):
    log.debug(("sender", sender, "kwargs", kwargs))
    subscription = kwargs.get('instance')
    log.debug("Subscription was just canceled. Creating a notification.")
    notif_type, _ = NotificationType.objects.get_or_create(name="subscription.deleted",
                                                           defaults={'entity': "billing"})
    notification = Notification(user=kwargs.get('user'),
                                actor=kwargs.get('actor'),
                                target=subscription,
                                type=notif_type)
    notification.save()
    log.debug("Created the notification")


@receiver(subscription_created, sender=Subscription)
def sub_created_handler(sender, **kwargs):
    log.debug(("sender", sender, "kwargs", kwargs))
    subscription = kwargs.get('instance')
    log.debug("Subscription was just Created. Creating a notification.")
    notif_type, _ = NotificationType.objects.get_or_create(name="subscription.created",
                                                           defaults={'entity': "billing"})
    notification = Notification(user=kwargs.get('user'),
                                actor=kwargs.get('actor'),
                                target=subscription,
                                type=notif_type)
    notification.save()
    log.debug("Created the notification")


@receiver(invoice_payment_success)
def invoice_payment_successful_handler(sender, **kwargs):
    subscription = kwargs.get('subscription')
    invoice = kwargs.get('invoice')
    notif_type, _ = NotificationType.objects.get_or_create(name="invoice.payment_succeeded",
                                                           defaults={'entity': "billing"})
    notification = Notification(user=invoice.customer.user,
                                actor=subscription,
                                target=invoice,
                                type=notif_type)
    notification.save()


@receiver(invoice_payment_failure)
def invoice_payment_failure_handler(sender, **kwargs):
    subscription = kwargs.get('subscription')
    invoice = kwargs.get('invoice')
    notif_type, _ = NotificationType.objects.get_or_create(name="invoice.payment_failed",
                                                           defaults={'entity': "billing"})
    notification = Notification(user=invoice.customer.user,
                                actor=subscription,
                                target=invoice,
                                type=notif_type)
    notification.save()
