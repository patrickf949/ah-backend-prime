from unittest.mock import patch, MagicMock

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from authors.apps.articles.tasks import delete_s3_image
from authors.apps.articles.tests.base import ArticlesBaseTest
from authors.apps.articles.tests.mocks import ExternalServicesMockMixin
from authors.apps.articles.tests.test_data import VALID_ARTICLE
from authors.apps.authentication.models import User
from authors.apps.authentication.tests.test_data import VALID_USER_DATA


class DraftCacheClearedTest(ArticlesBaseTest):
    """Publishing or updating an article clears the user's autosave draft."""

    def test_publishing_article_clears_draft(self):
        token = self.create_user(VALID_USER_DATA)
        response = self.create_article(VALID_ARTICLE, token)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=VALID_USER_DATA['user']['email'])
        self.mock_cache.delete.assert_called_once_with(
            f"draft:article:{user.id}")

    def test_updating_article_clears_draft(self):
        token = self.create_user(VALID_USER_DATA)
        slug = self.create_article(VALID_ARTICLE, token).data['article']['slug']
        self.mock_cache.reset_mock()

        response = self.client.put(
            reverse('crud-article', kwargs={'slug': slug}),
            data={'title': 'updated title'},
            HTTP_AUTHORIZATION=token,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.mock_cache.delete.assert_called_once()


class ImageDeleteTest(ExternalServicesMockMixin, APITestCase):
    """Deleting an uploaded image frees quota and queues the r2 deletion."""

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            username='imgowner', email='imgowner@test.com', password='password123')
        self.client.force_authenticate(user=self.user)
        self.upload_url = reverse('upload-image-url')

    def _create_upload(self, url):
        from authors.apps.profiles.models import UserImageUpload
        return UserImageUpload.objects.create(
            user=self.user, file_url=url, file_size_bytes=1024)

    def test_delete_image_queues_background_task(self):
        from authors.apps.profiles.models import UserImageUpload
        url = 'https://cdn.example.com/images/abc123.jpg'
        self._create_upload(url)

        response = self.client.delete(self.upload_url, {'url': url}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.mock_delete_image_task.delay.assert_called_once_with('images/abc123.jpg')
        self.assertFalse(UserImageUpload.objects.filter(file_url=url).exists())

    def test_delete_image_requires_url(self):
        response = self.client.delete(self.upload_url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.mock_delete_image_task.delay.assert_not_called()

    def test_delete_image_not_owned(self):
        response = self.client.delete(
            self.upload_url, {'url': 'https://cdn.example.com/images/x.jpg'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.mock_delete_image_task.delay.assert_not_called()

    def test_delete_image_invalid_url_format(self):
        url = 'https://cdn.example.com/other/x.jpg'
        self._create_upload(url)

        response = self.client.delete(self.upload_url, {'url': url}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.mock_delete_image_task.delay.assert_not_called()


class DeleteS3ImageTaskTest(APITestCase):
    """The celery task removes the object from r2 and never raises."""

    @patch('authors.apps.articles.tasks.boto3.client')
    def test_task_deletes_object(self, mock_client):
        s3 = MagicMock()
        mock_client.return_value = s3

        delete_s3_image('images/abc123.jpg')

        s3.delete_object.assert_called_once()
        self.assertEqual(s3.delete_object.call_args.kwargs['Key'], 'images/abc123.jpg')

    @patch('authors.apps.articles.tasks.boto3.client')
    def test_task_swallows_s3_errors(self, mock_client):
        mock_client.return_value.delete_object.side_effect = Exception('boom')

        # should not raise
        delete_s3_image('images/abc123.jpg')
