from django.urls import reverse
from authors.apps.authentication.tests.base import BaseTest
from authors.apps.articles.tests.mocks import ExternalServicesMockMixin


class NotificationBaseTest(ExternalServicesMockMixin, BaseTest):
    def setUp(self):
        super().setUp()
        self.notification_url = reverse('notifications')
        self.notification_unread_url = reverse('notifications-unread')