import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.db.models.signals import pre_save
from django.dispatch import receiver
from billing.models import Customer, Plan
from billing.stripe_utils import (create_stripe_customer_from_user,
                                  create_plan_in_stripe,
                                  assign_customer_to_default_plan,
                                  update_plan_in_stripe)
log = logging.getLogger("billing")


@receiver(post_save, sender=get_user_model())
def check_if_customer_exists_for_user(sender, instance, created, **kwargs):
    user = instance
    if settings.ENABLE_BILLING:
        try:
            user.customer
        except Customer.DoesNotExist:
            log.info("No stripe customer exists for user {uname}. "
                     "Creating one.".format(uname=user.username))
            customer = create_stripe_customer_from_user(user)
            assign_customer_to_default_plan(customer)
