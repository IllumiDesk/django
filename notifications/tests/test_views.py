import logging
from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.tests.factories import UserFactory, EmailFactory

from notifications.models import Notification, NotificationSettings
from .factories import NotificationFactory, NotificationSettingsFactory
log = logging.getLogger('notifications')


class NotificationsViewTest(APITestCase):

    def setUp(self):
        self.user = UserFactory()
        self.token_header = "Token {auth}".format(auth=self.user.auth_token.key)
        self.client = self.client_class(HTTP_AUTHORIZATION=self.token_header)

    def test_list_notifications_no_params(self):
        # It's obviously nonsensical to have the actor and target both be
        # self.user here, but this is the simplest way to just generate notifications
        NotificationFactory.create_batch(3, user=self.user,
                                         actor=self.user,
                                         target=self.user)
        url = reverse("notification-list", kwargs={'version': settings.DEFAULT_VERSION,
                                                   'namespace': self.user.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_list_notifications_filter_by_entity(self):
        NotificationFactory.create_batch(2, user=self.user,
                                         actor=self.user,
                                         target=self.user)
        notif = NotificationFactory(user=self.user,
                                    actor=self.user,
                                    target=self.user)
        NotificationFactory.create_batch(3, user=self.user,
                                         actor=self.user,
                                         target=self.user,
                                         type=notif.type)

        url = reverse("notification-with-entity-list", kwargs={'version': settings.DEFAULT_VERSION,
                                                               'namespace': self.user.username,
                                                               'entity': notif.type.entity})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    def test_get_notification_detail(self):
        notif = NotificationFactory(user=self.user,
                                    actor=self.user,
                                    target=self.user)
        url = reverse("notification-detail", kwargs={'version': settings.DEFAULT_VERSION,
                                                     'namespace': self.user.username,
                                                     'pk': str(notif.pk)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(notif.pk))

    def test_get_notification_detail_with_entity(self):
        notif = NotificationFactory(user=self.user,
                                    actor=self.user,
                                    target=self.user)
        url = reverse("notification-with-entity-detail", kwargs={'version': settings.DEFAULT_VERSION,
                                                                 'namespace': self.user.username,
                                                                 'entity': notif.type.entity,
                                                                 'pk': str(notif.pk)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(notif.pk))

    def test_get_notification_detail_with_different_entity_is_not_found(self):
        notif = NotificationFactory(user=self.user,
                                    actor=self.user,
                                    target=self.user)
        url = reverse("notification-with-entity-detail", kwargs={'version': settings.DEFAULT_VERSION,
                                                                 'namespace': self.user.username,
                                                                 'entity': "foo",
                                                                 'pk': str(notif.pk)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_marking_single_notification_read(self):
        notif = NotificationFactory(user=self.user,
                                    actor=self.user,
                                    target=self.user)
        url = reverse("notification-with-entity-detail", kwargs={'version': settings.DEFAULT_VERSION,
                                                                 'namespace': self.user.username,
                                                                 'entity': notif.type.entity,
                                                                 'pk': str(notif.pk)})
        data = {'read': True}
        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notif_reloaded = Notification.objects.get(pk=notif.pk)
        self.assertTrue(notif_reloaded.read)

    def test_marking_list_of_notifications_read(self):
        notif = NotificationFactory(user=self.user,
                                    actor=self.user,
                                    target=self.user,
                                    read=False)
        NotificationFactory.create_batch(3,
                                         user=self.user,
                                         actor=self.user,
                                         target=self.user,
                                         type=notif.type,
                                         read=False)
        to_update = Notification.objects.filter(type=notif.type).values_list('pk', flat=True)
        NotificationFactory.create_batch(5,
                                         user=self.user,
                                         actor=self.user,
                                         target=self.user,
                                         read=False)
        url = reverse("notification-with-entity-list", kwargs={'version': settings.DEFAULT_VERSION,
                                                               'namespace': self.user.username,
                                                               'entity': notif.type.entity})
        data = {'read': True,
                'notifications': list(map(str, to_update))}
        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        read_notifs = Notification.objects.filter(user=self.user,
                                                  read=True)
        self.assertEqual(read_notifs.count(), 4)
        read_notif_types = set(read_notifs.values_list('type__entity', flat=True))
        self.assertEqual(read_notif_types, {notif.type.entity})

        unread_notifs = Notification.objects.filter(user=self.user,
                                                    read=False)
        self.assertEqual(unread_notifs.count(), 5)

    def test_updating_single_notification_without_entity(self):
        notif = NotificationFactory(user=self.user,
                                    actor=self.user,
                                    target=self.user,
                                    read=True)
        url = reverse("notification-detail", kwargs={'version': settings.DEFAULT_VERSION,
                                                     'namespace': self.user.username,
                                                     'pk': str(notif.pk)})
        data = {'read': False}
        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notif_reloaded = Notification.objects.get(pk=notif.pk)
        self.assertFalse(notif_reloaded.read)

    def test_updating_list_of_notifications_without_entity(self):
        notifs = NotificationFactory.create_batch(3,
                                                  user=self.user,
                                                  actor=self.user,
                                                  target=self.user,
                                                  read=True)
        to_update = [str(n.pk) for n in notifs]
        NotificationFactory.create_batch(5,
                                         user=self.user,
                                         actor=self.user,
                                         target=self.user,
                                         read=True)
        url = reverse("notification-list", kwargs={'version': settings.DEFAULT_VERSION,
                                                   'namespace': self.user.username})
        data = {'read': False,
                'notifications': to_update}
        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        read_notifs = Notification.objects.filter(user=self.user,
                                                  read=True)
        self.assertEqual(read_notifs.count(), 5)

        unread_notifs = Notification.objects.filter(user=self.user,
                                                    read=False)
        self.assertEqual(unread_notifs.count(), 3)


class NotificationSettingsViewTest(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.email = EmailFactory(user=self.user,
                                  address=self.user.email)
        self.token_header = "Token {auth}".format(auth=self.user.auth_token.key)
        self.client = self.client_class(HTTP_AUTHORIZATION=self.token_header)

    def test_create_notification_settings(self):
        url = reverse("notification-settings", kwargs={'version': settings.DEFAULT_VERSION,
                                                       'namespace': self.user.username})
        data = {'enabled': True,
                'emails_enabled': True,
                'email_address': str(self.email.pk)}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        notif_settings = NotificationSettings.objects.filter(user=self.user,
                                                             entity="global").first()
        self.assertIsNotNone(notif_settings)
        self.assertTrue(notif_settings.enabled)
        self.assertTrue(notif_settings.emails_enabled)
        self.assertEqual(notif_settings.email_address, self.email)

    def test_partial_update_notification_settings(self):
        NotificationSettingsFactory(user=self.user,
                                    entity="global",
                                    enabled=True)
        url = reverse("notification-settings", kwargs={'version': settings.DEFAULT_VERSION,
                                                       'namespace': self.user.username})
        data = {'enabled': False}
        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notif_settings = NotificationSettings.objects.filter(user=self.user,
                                                             entity="global").first()
        self.assertFalse(notif_settings.enabled)

    def test_notification_settings_retrieve(self):
        notif_settings = NotificationSettingsFactory(user=self.user,
                                                     entity="global",
                                                     enabled=True)
        url = reverse("notification-settings", kwargs={'version': settings.DEFAULT_VERSION,
                                                       'namespace': self.user.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        log.debug(response.data)
        self.assertEqual(response.data['id'], str(notif_settings.pk))

    def test_notification_settings_delete(self):
        NotificationSettingsFactory(user=self.user,
                                    entity="global",
                                    enabled=True)
        url = reverse("notification-settings", kwargs={'version': settings.DEFAULT_VERSION,
                                                       'namespace': self.user.username})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        notif_settings_count = NotificationSettings.objects.filter(user=self.user).count()
        self.assertEqual(notif_settings_count, 0)
