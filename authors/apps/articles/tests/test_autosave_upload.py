from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from authors.apps.authentication.models import User

class AutoSaveAndUploadTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser123', email='test1234@test.com', password='password123')
        self.client.force_authenticate(user=self.user)
        self.autosave_url = reverse('article-autosave')
        self.upload_url = reverse('upload-image-url')

    @patch('authors.apps.articles.views.cache')
    def test_autosave_draft_post(self, mock_cache):
        data = {'title': 'Draft', 'body': 'Draft body'}
        response = self.client.post(self.autosave_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(mock_cache.set.called)
        
    @patch('authors.apps.articles.views.cache')
    def test_autosave_draft_get_exists(self, mock_cache):
        mock_cache.get.return_value = {'title': 'Draft', 'body': 'Draft body'}
        response = self.client.get(self.autosave_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['draft']['title'], 'Draft')
        self.assertTrue(mock_cache.get.called)

    @patch('authors.apps.articles.views.cache')
    def test_autosave_draft_get_empty(self, mock_cache):
        mock_cache.get.return_value = None
        response = self.client.get(self.autosave_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'No draft found.')
        self.assertTrue(mock_cache.get.called)

    @patch('authors.apps.articles.views.boto3.client')
    def test_upload_image_url_success(self, mock_boto_client):
        # Mock the S3 client and generate_presigned_url
        mock_s3 = mock_boto_client.return_value
        mock_s3.generate_presigned_url.return_value = "https://mock-presigned-url.com"
        
        data = {'filename': 'test.jpg', 'contentType': 'image/jpeg', 'size': 102400}
        response = self.client.post(self.upload_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("uploadUrl", response.data)
        self.assertEqual(response.data["uploadUrl"], "https://mock-presigned-url.com")
        self.assertTrue(mock_s3.generate_presigned_url.called)

    def test_upload_image_invalid_type(self):
        data = {'filename': 'test.pdf', 'contentType': 'application/pdf', 'size': 102400}
        response = self.client.post(self.upload_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Only images are allowed.")

    def test_upload_image_missing_fields(self):
        data = {'filename': 'test.jpg'}
        response = self.client.post(self.upload_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "filename, contentType, and size are required.")
        
    def test_upload_image_exceeds_500kb(self):
        data = {'filename': 'test.jpg', 'contentType': 'image/jpeg', 'size': 600 * 1024}
        response = self.client.post(self.upload_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Image size exceeds the 500KB limit.")
        
    def test_upload_image_exceeds_quota(self):
        from authors.apps.profiles.models import UserImageUpload
        UserImageUpload.objects.create(user=self.user, file_url='http://test', file_size_bytes=9.6 * 1024 * 1024)
        
        data = {'filename': 'test.jpg', 'contentType': 'image/jpeg', 'size': 500 * 1024} # 500KB on top of 9.6MB > 10MB
        response = self.client.post(self.upload_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Upload would exceed your 10MB total quota.")
