import logging
import math
from datetime import datetime, timedelta
from decimal import Decimal, getcontext
from django.conf import settings
from django.db.models import (Q, Sum, F, DurationField,
                              Case, When, ExpressionWrapper)
from django.db.models.functions import Greatest
from django.utils import timezone
from billing.models import Invoice
from billing.stripe_utils import add_buckets_to_stripe_invoice
from servers.models import ServerRunStatistics
from notifications.models import Notification, NotificationType
from notifications.utils import create_notification
log = logging.getLogger('servers')
getcontext().prec = 6


class MeteredBillingData:
    def __init__(self, user, invoice, usage):
        self.user = user
        self.invoice = invoice
        self.subscription = invoice.subscription
        self.plan_limit = self.subscription.plan.metadata.get('gb_hours')
        self.usage = usage
        self.usage_percent = Decimal((self.usage / self.plan_limit) * 100)

    def __str__(self):
        return f"{self.user}: {self.usage} GB of {self.plan_limit} GB - {self.usage_percent}%."

    def calc_necessary_buckets(self) -> int:
        buckets = 0
        overage = self.usage - self.plan_limit
        if overage > 0:
            buckets = math.ceil(overage / settings.BILLING_BUCKET_SIZE_GB)
        return buckets

    def create_notification_if_necessary(self, notification_type: NotificationType) -> Notification:
        notif = None

        try:
            warning_thresholds = sorted(map(int, settings.USAGE_WARNING_THRESHOLDS.split(",")),
                                        # We sort in reverse order because it's easier to notify in order of
                                        # precedence later in this method.
                                        key=lambda val: -val)
        except ValueError as e:
            log.warning(f"Unable to cast USAGE_WARNING_THRESHOLDS to a list of ints. "
                        f"This was the value: {settings.USAGE_WARNING_THRESHOLDS}. "
                        f"Falling back to defaults of 75, 90, 100.")
            log.exception(e)
            warning_thresholds = [75, 90, 100]

        for threshold in warning_thresholds:
            if self.usage_percent >= threshold:
                already_been_notified = Notification.objects.filter(user=self.user,
                                                                    type=notification_type,
                                                                    timestamp__gt=self.invoice.period_start).exists()
                if not already_been_notified:
                    log.info(f"User {self.user} has used {self.usage_percent}% of their plan. Sending a notification.")
                    notif = create_notification(user=self.user,
                                                actor=self.invoice,
                                                target=None,
                                                notif_type=notification_type)
                    break
        return notif


def calculate_usage_for_period(closing_from: datetime=None, closing_to: datetime=None) -> dict:
    """
    :return: user_runs_mapping is a dict that maps user.pk -> 
             Percentage of plan used for this billing period. 
    """
    notification_type = NotificationType.objects.get(name="usage_warning")
    # TODO: In theory there is only one open invoice per user, but this needs to be verified, especially for teams
    invoices = Invoice.objects.filter(closed=False)

    if closing_from:
        invoices = invoices.filter(period_end__gte=closing_from)
    if closing_to:
        invoices = invoices.filter(period_end__lte=closing_to)

    invoices = invoices.select_related('customer__user', 'subscription__plan')

    user_runs_mapping = {}
    notifs_to_save = []
    for inv in invoices:
        user = inv.customer.user

        if user.pk in user_runs_mapping:
            log.warning(f"For some reason {user} currently has multiple open invoices. "
                        f"This shouldn't really happen, and I'm not sure how to handle it for now.")

        """ 
            The complicated Django query that follows is necessary for performance reasons.
            For the sake of clarity, here is a python-only implementation:
            runs = ServerRunStatistics.objects.filter(Q(stop=None) | Q(start__gte=inv.period_start),
                                                  owner=inv.customer.user)
            this_user_total = 0.0
            for run in runs:
                # If a run has not been stopped yet, use timezone.now() as the cutoff
                # If a run started before the current billing period, use inv.period_start as the beginning,
                # as we only want to bill for usage that has occurred in this period.
                run_duration = ((run.stop or timezone.now()) - max(inv.period_start, run.start)).total_seconds()
    
                # server_size_memory is in megabytes, so divide to get GB
                # run_duration is in seconds, so divide to get hours
                this_run_gb_hours = (run.server_size_memory / 1024) * (run_duration / 3600)
                this_user_total += this_run_gb_hours
        """

        user_runs = ServerRunStatistics.objects.filter(Q(stop=None) | Q(stop__gte=inv.period_start),
                                                       owner=inv.customer.user)
        cust_start = inv.customer.last_invoice_sync or inv.period_start
        usage_in_mb_seconds = user_runs.aggregate(usage=Sum(Case(When(stop__isnull=False,
                                                                      then=ExpressionWrapper((F('stop') - Greatest(
                                                                          F('start'), cust_start)) * F(
                                                                          'server_size_memory'),
                                                                                             output_field=DurationField())),
                                                                 When(stop__isnull=True,
                                                                      then=ExpressionWrapper((timezone.now() - Greatest(
                                                                          F('start'), cust_start)) * F(
                                                                          'server_size_memory'),
                                                                                             output_field=DurationField())
                                                                      )
                                                                 ),
                                                            output_field=DurationField()))['usage']
        if usage_in_mb_seconds is not None:
            usage_in_mb_seconds = Decimal(usage_in_mb_seconds.total_seconds())
            # Divide by 1024 to get gigabytes, then 3600 to get hours. MB Seconds -> GB Hours
            usage_in_gb_hours = Decimal(usage_in_mb_seconds / 1024 / 3600)
            usage_data = MeteredBillingData(user=user,
                                            invoice=inv,
                                            usage=usage_in_gb_hours)
            user_runs_mapping[user.pk] = usage_data

            notif = usage_data.create_notification_if_necessary(notification_type)
            if notif is not None:
                notifs_to_save.append(notif)

    Notification.objects.bulk_create(notifs_to_save)
    return user_runs_mapping


def update_invoices_with_usage(ending_in: int=30):
    end_time = timezone.now() + timedelta(seconds=ending_in * 60)
    current_usage_map = calculate_usage_for_period(closing_from=timezone.now(),
                                                   closing_to=end_time)
    # Something in the following loop is using a LOT of time. is it the Stripe call?
    # No, I'm mocking stripe at the moment.
    for user in current_usage_map:
        data_entry = current_usage_map[user]
        # TODO: Need to add provisions to handle metered instances
        buckets_needed = data_entry.calc_necessary_buckets()
        if buckets_needed > 0:
            log.info(f"User {data_entry.user} needs {buckets_needed} bucket(s). "
                     f"Adding them to their invoice.")
            invoice_item = add_buckets_to_stripe_invoice(data_entry.user.customer.stripe_id,
                                                         buckets_needed)
            log.info(f"Successfully created invoice_item {invoice_item.stripe_id}.")

        data_entry.user.customer.last_invoice_sync = timezone.now()
        data_entry.user.customer.save()