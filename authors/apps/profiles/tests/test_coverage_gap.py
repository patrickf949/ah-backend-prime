from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from authors.apps.authentication.models import User
from authors.apps.profiles.models import Profile, UserImageUpload


class ProfilesCoverageGapTest(APITestCase):
    """Covers missing lines in profiles models and views."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='profilegapuser', email='profilegap@example.com', password='password123'
        )

    def test_profiles_models_str(self):
        profile = self.user.profile
        self.assertEqual(str(profile), self.user.username)

        upload = UserImageUpload.objects.create(
            user=self.user,
            file_url='https://example.com/test.jpg',
            file_size_bytes=2048
        )
        self.assertIn(self.user.username, str(upload))
        self.assertIn('https://example.com/test.jpg', str(upload))

    def test_retrieve_nonexistent_profile_404(self):
        url = reverse('get-profile', kwargs={'username': 'doesnotexist_ever'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_profile_unauthenticated_following_false(self):
        url = reverse('get-profile', kwargs={'username': self.user.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['profile'].get('following'), 'False')
