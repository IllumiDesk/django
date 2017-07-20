import shutil
import json
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from users.tests.factories import UserFactory, EmailFactory
from utils import create_ssh_key

User = get_user_model()


class UserTest(APITestCase):
    def setUp(self):
        self.admin = UserFactory(is_staff=True, username='admin')
        self.user = UserFactory(username='user')
        self.admin_client = self.client_class(HTTP_AUTHORIZATION='Token {}'.format(self.admin.auth_token.key))
        self.user_client = self.client_class(HTTP_AUTHORIZATION='Token {}'.format(self.user.auth_token.key))
        self.to_remove = None

    def tearDown(self):
        if self.to_remove is not None:
            shutil.rmtree(str(self.to_remove))

    def test_user_delete_by_admin(self):
        user = UserFactory()
        # For whatever reason, create_ssh_key doesnt seem to be called by the Factory here.
        # It doesn't matter, we just need the directory to exist.
        create_ssh_key(user)
        url = reverse('user-detail', kwargs={'pk': str(user.pk),
                                             'version': settings.DEFAULT_VERSION})
        response = self.admin_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_delete_by_user(self):
        user = UserFactory()
        url = reverse('user-detail', kwargs={'pk': str(user.pk),
                                             'version': settings.DEFAULT_VERSION})
        response = self.user_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_user_without_profile(self):
        user = UserFactory()
        url = reverse("user-detail", kwargs={'pk': user.pk,
                                             'version': settings.DEFAULT_VERSION})
        data = {'first_name': "Tom"}
        response = self.admin_client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_reloaded = User.objects.get(pk=user.pk)
        self.assertEqual(user_reloaded.first_name, "Tom")

    def test_user_delete_allows_new_user_with_same_username(self):
        user = UserFactory()
        create_ssh_key(user)

        username = user.username
        url = reverse('user-detail', kwargs={'pk': str(user.pk),
                                             'version': settings.DEFAULT_VERSION})
        response = self.admin_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        old_user = User.objects.get(username=username,
                                    is_active=False)
        self.assertIsNotNone(old_user)

        url = reverse("user-list", kwargs={'version': settings.DEFAULT_VERSION})
        data = {'username': user.username,
                'email': "foo@example.com",
                'first_name': "Foo",
                'last_name': "Bar",
                'password': "password",
                'profile': {}}
        response = self.admin_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_user_reloaded = User.objects.get(username=username,
                                             is_active=True)
        self.assertIsNotNone(new_user_reloaded)

        self.assertNotEqual(old_user.pk, new_user_reloaded.pk)
        self.to_remove = new_user_reloaded.profile.resource_root()

    def test_creating_user_with_matching_active_user_fails(self):
        url = reverse("user-list", kwargs={'version': settings.DEFAULT_VERSION})
        data = {'username': self.user.username,
                'email': "foo@example.com",
                'first_name': "Foo",
                'last_name': "Bar",
                'password': "password",
                'profile': {}}
        response = self.admin_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        expected_error = "{username} is already taken.".format(username=self.user.username)
        error_list = response.data.get('username')
        self.assertEqual(len(error_list), 1)
        self.assertEqual(error_list[0], expected_error)


class EmailTest(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client = self.client_class(HTTP_AUTHORIZATION='Token {}'.format(self.user.auth_token.key))

    def test_list_has_access_to_all_my_emails(self):
        EmailFactory(public=True, user=self.user)
        EmailFactory(public=False, user=self.user)

        url = reverse("email-list", kwargs={'user_id': self.user.pk,
                                            'version': settings.DEFAULT_VERSION})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_emails_gets_correct_ones(self):
        other_email_public = EmailFactory(public=True)
        other_email_private = EmailFactory(public=False,
                                           user=other_email_public.user)

        url = reverse("email-list", kwargs={'user_id': other_email_private.user.pk,
                                            'version': settings.DEFAULT_VERSION})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        resp_email = response.data[0]
        self.assertEqual(resp_email['address'], other_email_public.address)
        self.assertTrue(resp_email['public'])

    def test_retrieve_doesnt_get_private_emails(self):
        other_email_private = EmailFactory(public=False,)

        url = reverse("email-detail", kwargs={'user_id': other_email_private.user.pk,
                                              'pk': other_email_private.pk,
                                              'version': settings.DEFAULT_VERSION})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class UserIntegrationTest(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client = self.client_class(HTTP_AUTHORIZATION='Token {}'.format(self.user.auth_token.key))

    def test_creating_integration(self):
        url = reverse("usersocialauth-list", kwargs={'version':settings.DEFAULT_VERSION})
        data = {'provider': "github",
                'extra_data': json.dumps({'foo': "Bar"})}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get("provider"), "github")
        self.assertEqual(json.loads(response.data.get("extra_data")), {'foo': "Bar"})
