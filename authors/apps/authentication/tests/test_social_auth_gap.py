from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from authors.apps.authentication.models import User
from authors.apps.social_auth.google_auth import GoogleAuthHandler
from authors.apps.social_auth.models import SocialAccount
from authors.apps.social_auth.twitter_auth import TwitterAuthHandler


class SocialAuthCoverageGapTest(APITestCase):
    """Covers missing lines in social_auth models, helpers, and views."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='socialgapuser', email='socialgap@example.com', password='password123'
        )

    def test_social_account_str(self):
        account = SocialAccount.objects.create(
            user=self.user,
            provider='google',
            provider_user_id='google-123456'
        )
        self.assertIn('google:google-123456', str(account))

    @patch('authors.apps.social_auth.google_auth.id_token.verify_oauth2_token')
    def test_google_auth_wrong_issuer(self, mock_verify):
        mock_verify.return_value = {
            'iss': 'untrusted-issuer.com',
            'sub': '123',
            'email': 'evil@example.com'
        }
        res = GoogleAuthHandler.validate_google_auth_token('fake-token')
        self.assertEqual(res, 'This token is invalid')

    def test_twitter_auth_single_token(self):
        res = TwitterAuthHandler.validate_twitter_auth_tokens('single_token_only')
        self.assertEqual(res, "Invalid. Please provide two tokens!")

    @patch('authors.apps.social_auth.twitter_auth.twitter.Api')
    def test_twitter_auth_success(self, mock_api_class):
        mock_api = MagicMock()
        class DummyUser:
            def __init__(self):
                self.email = 'tw@example.com'
                self.name = 'Twitter User'
        mock_api.VerifyCredentials.return_value = DummyUser()
        mock_api_class.return_value = mock_api

        res = TwitterAuthHandler.validate_twitter_auth_tokens('token_key token_secret')
        self.assertEqual(res, {'email': 'tw@example.com', 'name': 'Twitter User'})

    @patch('authors.apps.social_auth.twitter_auth.TwitterAuthHandler.validate_twitter_auth_tokens')
    def test_twitter_auth_view_post(self, mock_validate):
        mock_validate.return_value = {
            'id_str': '12345678',
            'email': 'twuser@example.com',
            'name': 'Twitter User'
        }
        response = self.client.post(
            '/api/v1/social/auth/twitter/',
            {'user_token': {'auth_token': 'tok1 tok2'}},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('auth_token', response.data)
        self.assertEqual(response.data['auth_token'].get('email'), 'twuser@example.com')
