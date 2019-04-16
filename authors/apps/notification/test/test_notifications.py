from django.urls import reverse
from django.shortcuts import get_object_or_404
from rest_framework import status
from authors.apps.authentication.tests.test_data import VALID_USER_DATA
from authors.apps.articles.tests.test_data import VALID_ARTICLE
from authors.apps.notification.test.base import NotificationBaseTest
from authors.apps.notification.test.test_data import VALID_USER_DATA_2
from authors.apps.notification.models import Notification


class TestNotifications(NotificationBaseTest):
    def test_get_all_notifications(self):
        token = self.create_user(VALID_USER_DATA)
        token2 = self.create_user(VALID_USER_DATA_2)
        self.client.post(
            reverse('follow-profile', kwargs={'username': 'anyatijude'}),
            HTTP_AUTHORIZATION=token2
        )
        response = self.client.post(
            reverse('articles'),
            data=VALID_ARTICLE,
            format='json',
            HTTP_AUTHORIZATION=token
        )
        self.client.post(
            reverse('favorite-article', kwargs={'slug': response.data['article']['slug']}),
            format='json'
        )
        self.client.post(reverse(
            'comments',
            kwargs={'slug': response.data['article']['slug'], 'id': 0}),
            data={"body": "the was lms was fine"},
            format='json')
        response = self.client.get(
            self.notification_url,
            format='json',
            HTTP_AUTHORIZATION=token2
        )
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_get_single_unread_notification(self):
        """
        test that returns all the unread notifications
        """
        token = self.create_user(VALID_USER_DATA)
        token2 = self.create_user(VALID_USER_DATA_2)
        self.client.post(
            reverse('follow-profile', kwargs={'username': 'anyatijude'}),
            HTTP_AUTHORIZATION=token2
        )
        response_data = self.client.post(
            reverse('articles'),
            data=VALID_ARTICLE,
            format='json',
            HTTP_AUTHORIZATION=token
        )
        self.client.post(
            reverse('favorite-article',
                    kwargs={'slug': response_data.data['article']['slug']}),
            format='json'
        )
        self.client.post(reverse(
            'comments',
            kwargs={'slug': response_data.data['article']['slug'], 'id': 0}),
            data={"body": "the was lms was fine"},
            format='json')
        notifications = get_object_or_404(Notification)
        response = self.client.get(
            reverse('notification-detail', kwargs={'pk': notifications.pk}),
            format='json',
            HTTP_AUTHORIZATION=token2
        )
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data, response.data)

    def test_get_unread_notifications(self):
        """
        test that returns all the unread notifications
        """
        token = self.create_user(VALID_USER_DATA)
        token2 = self.create_user(VALID_USER_DATA_2)
        self.client.post(
            reverse('follow-profile', kwargs={'username': 'anyatijude'}),
            HTTP_AUTHORIZATION=token2
        )
        response_data = self.client.post(
            reverse('articles'),
            data=VALID_ARTICLE,
            format='json',
            HTTP_AUTHORIZATION=token
        )
        self.client.post(
            reverse('favorite-article',
                    kwargs={'slug': response_data.data['article']['slug']}),
            format='json'
        )
        self.client.post(reverse(
            'comments',
            kwargs={'slug': response_data.data['article']['slug'], 'id': 0}),
            data={"body": "the was lms was fine"},
            format='json')

        response = self.client.get(
            reverse('notifications-unread'),
            format='json',
            HTTP_AUTHORIZATION=token2
        )
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data, response.data)

    def test_single_notifications_not_found(self):
        """
        test that returns all the unread notifications
        """
        token = self.create_user(VALID_USER_DATA)
        token2 = self.create_user(VALID_USER_DATA_2)
        self.client.post(
            reverse('follow-profile', kwargs={'username': 'anyatijude'}),
            HTTP_AUTHORIZATION=token2
        )
        response_data = self.client.post(
            reverse('articles'),
            data=VALID_ARTICLE,
            format='json',
            HTTP_AUTHORIZATION=token
        )
        self.client.post(
            reverse('favorite-article',
                    kwargs={'slug': response_data.data['article']['slug']}),
            format='json'
        )
        self.client.post(reverse(
            'comments',
            kwargs={'slug': response_data.data['article']['slug'], 'id': 0}),
            data={"body": "the was lms was fine"},
            format='json')
        response = self.client.get(
            reverse('notification-detail', kwargs={'pk': 50}),
            format='json',
            HTTP_AUTHORIZATION=token2
        )

        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEquals(response.data['error'], 'notifications not available')

    def test_in_app_and_email_notification_disabled(self):
        token = self.create_user(VALID_USER_DATA)
        response = self.client.put(reverse('notification-disable'),
                                   HTTP_AUTHORIZATION=token,
                                   format='json'
                                   )
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data['error'], "disabled notifications app")
