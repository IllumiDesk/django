from django.conf import settings
from django.urls import reverse
from django.test import override_settings
from rest_framework.test import APITestCase
from users.tests.factories import UserFactory
from rest_framework import status
from billing.tests.factories import SubscriptionFactory


class TestMiddleware(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.user.is_staff = False
        self.user.save()
        self.token_header = "Token {auth}".format(auth=self.user.auth_token.key)
        self.client = self.client_class(HTTP_AUTHORIZATION=self.token_header)
        self.customer = self.user.customer

    @override_settings(ENABLE_BILLING=True)
    def test_no_subscription_is_rejected(self):
        url = reverse("project-list", kwargs={'version': settings.DEFAULT_VERSION,
                                              'namespace': self.user.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

    @override_settings(ENABLE_BILLING=True)
    def test_valid_subscription_accepted(self):
        SubscriptionFactory(customer=self.customer,
                            status="active")
        url = reverse("project-list", kwargs={'version': settings.DEFAULT_VERSION,
                                              'namespace': self.user.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
