import stripe
import logging
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from billing.models import Customer, Card
from users.tests.factories import UserFactory
from billing.tests.factories import CustomerFactory
from billing.stripe_utils import create_stripe_customer_from_user

log = logging.getLogger('billing')
stripe.api_key = settings.STRIPE_SECRET_KEY


class CustomerTest(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.token_header = "Token {auth}".format(auth=self.user.auth_token.key)
        self.client = self.client_class(HTTP_AUTHORIZATION=self.token_header)
        self.customers_to_delete = []

    def tearDown(self):
        for customer in self.customers_to_delete:
            stripe_obj = stripe.Customer.retrieve(customer.stripe_id)
            stripe_obj.delete()

    def test_create_customer(self):
        url = reverse("customer-list", kwargs={'namespace': self.user.username})
        data = {'user': self.user.pk}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 1)
        self.assertEqual(Customer.objects.get().user, self.user)
        self.customers_to_delete = [Customer.objects.get()]

    def test_list_customers(self):
        customers_count = 4
        customers = CustomerFactory.create_batch(customers_count)
        url = reverse("customer-list", kwargs={'namespace': self.user.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), customers_count)
        # Feels like we need more assertions here...

    def test_customer_details(self):
        customer = CustomerFactory(user=self.user)
        url = reverse("customer-detail", kwargs={'namespace': self.user.username,
                                                 'pk': customer.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(customer.pk), response.data.get('id'))

    def test_customer_update(self):
        customer = create_stripe_customer_from_user(self.user)
        self.customers_to_delete = [customer]
        url = reverse("customer-detail", kwargs={'namespace': self.user.username,
                                                 'pk': customer.pk})

        # TODO: Figure out how to only require user on create. Seems to require two serializers, which blech
        data = {'account_balance': 5000, 'user': str(self.user.pk)}
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        customer_reloaded = Customer.objects.get(pk=customer.pk)
        self.assertEqual(customer_reloaded.account_balance, 5000)

    def test_customer_delete(self):
        User = get_user_model()
        pre_del_user_count = User.objects.count()

        # Note that this customer is purposefully not being added to self.customers_to_delete
        # Deleting it from stripe is part of the test, obviously.
        customer = create_stripe_customer_from_user(self.user)
        url = reverse("customer-detail", kwargs={'namespace': self.user.username,
                                                 'pk': customer.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Customer.objects.count(), 0)

        post_del_user_count = User.objects.count()
        self.assertEqual(post_del_user_count, pre_del_user_count)
