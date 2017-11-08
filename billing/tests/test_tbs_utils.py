import random
from datetime import timedelta
from django.db.models import Sum, F, DurationField
from django.utils import timezone
from django.test import TestCase
from users.models import User
from users.tests.factories import UserFactory
from billing.stripe_utils import create_stripe_customer_from_user
from billing.tbs_utils import calculate_usage_for_current_billing_period
from billing.tests.factories import (PlanFactory,
                                     SubscriptionFactory,
                                     InvoiceFactory)
from notifications.models import Notification
from projects.tests.factories import CollaboratorFactory
from servers.models import ServerRunStatistics
from servers.tests.factories import ServerRunStatisticsFactory
import logging
log = logging.getLogger('servers')


class TestTbsUtils(TestCase):
    fixtures = ['notification_types.json']

    def setUp(self):
        self.user = UserFactory()
        self.customer = create_stripe_customer_from_user(self.user)
        self.plan = PlanFactory(interval="month",
                                interval_count=1,
                                metadata={'gb_hours': 5})

    def _setup_basics_for_user(self, user: User, duration: int=1, server_memory: int=512) -> ServerRunStatistics:
        log.debug("in setup basics for user")
        subscription = SubscriptionFactory(customer=user.customer,
                                           plan=self.plan)
        # Just so period_start and period_end are relative to the exact same time...
        now = timezone.now()
        InvoiceFactory(customer=user.customer,
                       subscription=subscription,
                       period_start=now - timedelta(days=15),
                       period_end=now + timedelta(days=15),
                       closed=False)
        project = CollaboratorFactory(user=user).project

        start_time = now - timedelta(hours=duration)
        return ServerRunStatisticsFactory(server__project=project,
                                          server__server_size__memory=server_memory,
                                          start=start_time,
                                          stop=now)

    def test_calc_usage_for_billing_period_simplest_case(self):
        # Only one user, with one invoice, one server, one run.
        self._setup_basics_for_user(self.user)
        usage_dict = calculate_usage_for_current_billing_period()
        self.assertEqual(usage_dict[self.user.pk], 10.0)

    def test_calc_usage_sends_notification_after_threshold(self):
        self._setup_basics_for_user(self.user, duration=4, server_memory=1024)
        usage_dict = calculate_usage_for_current_billing_period()
        self.assertEqual(usage_dict[self.user.pk], 80.0)

        notification = Notification.objects.filter(user=self.user,
                                                   type__name="usage_warning")
        self.assertEqual(notification.count(), 1)

    def test_calc_usage_one_user_and_server_multiple_runs(self):
        run = self._setup_basics_for_user(self.user)
        ServerRunStatisticsFactory.create_batch(4,
                                                server=run.server)
        # At this point we have 5 runs of a 512 MB server, each one hour in duration.
        usage_dict = calculate_usage_for_current_billing_period()
        self.assertEqual(usage_dict[self.user.pk], 50.0)

    def test_calc_usage_one_user_multiple_servers_single_run_each(self):
        self._setup_basics_for_user(self.user)
        for x in range(4):
            project = CollaboratorFactory(user=self.user).project
            ServerRunStatisticsFactory(server__project=project,
                                       server__server_size__memory=1024)

        # We now have 5 servers, each belonging to a different project owned by self.user
        # each with a single run one hour long. One server is 512 MB, the rest are 1GB,
        # Meaning our usage should total 4.5GB = 90% and a notification

        usage_dict = calculate_usage_for_current_billing_period()
        self.assertEqual(usage_dict[self.user.pk], 90.0)

        notification = Notification.objects.filter(user=self.user,
                                                   type__name="usage_warning")
        self.assertEqual(notification.count(), 1)

    def test_one_user_multiple_servers_multiple_runs(self):
        self._setup_basics_for_user(self.user)
        for x in range(4):
            project = CollaboratorFactory(user=self.user).project
            run = ServerRunStatisticsFactory(server__project=project,
                                             server__server_size__memory=1024)
            ServerRunStatisticsFactory.create_batch(2,
                                                    server=run.server)
        usage_dict = calculate_usage_for_current_billing_period()
        # 512MB * 1HR + (4 * (1GB server * 3 runs of 1 hour)) = 12.5 GB/hrs = 250.0% usage
        self.assertEqual(usage_dict[self.user.pk], 250.0)

    def test_multiple_users_single_server_and_run(self):
        users = UserFactory.create_batch(4) + [self.user]
        for user in users:
            duration = random.randint(1, 3)
            self._setup_basics_for_user(user, duration=duration, server_memory=1024)

        # We now have 5 users, each with a single 1GB server that has run one time for 1, 2, or 3 hours.
        usage_dict = calculate_usage_for_current_billing_period()
        for user in users:
            run = ServerRunStatistics.objects.filter(owner=user).first()
            self.assertIsNotNone(run)
            expected_usage = ((run.duration.seconds / 3600) / 5) * 100
            self.assertEqual(usage_dict[user.pk], expected_usage)

    def test_multiple_users_multiple_servers_and_runs(self):
        users = UserFactory.create_batch(4) + [self.user]
        for user in users:
            run = self._setup_basics_for_user(user)
            log.debug(("run.owener", run.owner))
            log.debug(("run server memory", run.server_size_memory))
            log.debug(("run duration", run.duration))
            for x in range(4):
                project = CollaboratorFactory(user=user).project

                # duration = random.randint(1, 3)
                duration = 1
                now = timezone.now()
                start_time = now - timedelta(hours=duration)

                # run = ServerRunStatisticsFactory(server__project=project,
                #                                  server__server_size__memory=1024,
                #                                  start=start_time,
                #                                  stop=now)
                # ServerRunStatisticsFactory.create_batch(2, server=run.server, start=start_time, stop=now)

        usage_dict = calculate_usage_for_current_billing_period()
        for user in users:
            log.debug(("user", user))
            usage_in_byte_seconds = ServerRunStatistics.objects.filter(owner=
                                                                       user).aggregate(usage=Sum(F('duration') *
                                                                                                 (F('server_size_memory')),
                                                                                                 output_field=DurationField()))
            log.debug(("usage amount", usage_in_byte_seconds))
            log.debug(("days", usage_in_byte_seconds['usage'].days))
            log.debug(("seconds", usage_in_byte_seconds['usage'].seconds))
            log.debug(("microseconds", usage_in_byte_seconds['usage'].microseconds))

