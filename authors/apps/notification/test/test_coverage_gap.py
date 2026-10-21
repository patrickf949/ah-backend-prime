from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from authors.apps.articles.models import Articles, Comment, FavoriteArticle
from authors.apps.articles.tests.mocks import ExternalServicesMockMixin
from authors.apps.authentication.models import User
from authors.apps.notification.models import Notification, NotificationSetting


class NotificationCoverageGapTest(ExternalServicesMockMixin, APITestCase):
    """Covers missing lines in notification models and views."""

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            username='notifuser', email='notif@example.com', password='password123'
        )
        self.client.force_authenticate(user=self.user)

    def test_notification_models_str(self):
        setting = NotificationSetting.objects.get(user=self.user.profile)
        self.assertEqual(str(setting), "notification setting")

        notif = Notification.objects.create(
            receiver=self.user.profile, message="Test message", is_read=False
        )
        self.assertEqual(str(notif), "Test message")

    @patch('authors.apps.notification.models.send_mail')
    def test_notify_user_when_favorite_author_comments(self, mock_send_mail):
        other_user = User.objects.create_user(
            username='authoruser', email='author@example.com', password='password123'
        )
        article = Articles.objects.create(
            title='Sample Article Title',
            slug='sample-article-title',
            body='article body',
            description='article desc',
            author=other_user.profile
        )
        # self.user favorites the author's article
        FavoriteArticle.objects.create(favorited_by=self.user.profile, article=article)

        # when a comment is created by the favorited author
        Comment.objects.create(
            author=self.user.profile,
            article=article,
            body='new author comment',
            parentId=0
        )
        # Should create a notification and call send_mail
        self.assertTrue(Notification.objects.filter(receiver=self.user.profile).exists())

    def test_unread_notifications_empty_returns_404(self):
        Notification.objects.filter(receiver=self.user.profile).delete()
        url = reverse('notifications-unread')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('notifications not available', response.data.get('error', ''))
