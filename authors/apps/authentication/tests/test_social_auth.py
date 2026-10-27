from rest_framework import status
from django.urls import reverse
from .base import BaseTest
from unittest.mock import patch
from authors.apps.authentication.models import User, UserPassword
from authors.apps.social_auth.models import SocialAccount
from authors.apps.social_auth.register import register_social_user
from .test_data import (
    INVALID_GOOGLE_TOKEN,
    INVALID_FACEBOOK_TOKEN,
    INVALID_TWITTER_TOKENS,
    VALID_USER_DATA,
    VALID_SOCIAL_DATA,
    EMPTY_SOCIAL_EMAIL_DATA,
    VALID_USER_DATA_FOR_USER,
    VALID_LOGIN_DATA_FOR_USER
)


def google_mock(email='test@email.com', name='testname',
                sub='117589369073046072597'):
    """Builds a stand-in for google_auth.id_token returning fixed claims"""

    class MockGoogleAuth:

        @classmethod
        def verify_oauth2_token(cls, token, request, audience=None):
            return {
                'iss': 'accounts.google.com',
                'email': email,
                'name': name,
                'sub': sub
            }

    return MockGoogleAuth


class SocialAuthRegistration(BaseTest):
    """
    contains tests for social auth registration
    """

    def google_login(self, **claims):
        with patch('authors.apps.social_auth.google_auth.id_token',
                   new_callable=google_mock(**claims)):
            return self.client.post(
                '/api/v1/social/auth/google/',
                INVALID_GOOGLE_TOKEN,
                format='json'
            )

    def test_google_invalid_token(self):
        """ Test for invalid google token"""
        response = self.client.post(
            '/api/v1/social/auth/google/',
            INVALID_GOOGLE_TOKEN,
            format='json'
        )
        self.assertEqual(
            response.data['errors']['auth_token'][0],
            'This token is invalid'
        )

    def test_facebook_invalid_token(self):
        """Test for invalid facebook token"""
        response = self.client.post(
            '/api/v1/social/auth/facebook/',
            INVALID_FACEBOOK_TOKEN,
            format='json'
        )
        self.assertEqual(
            response.data['errors']['auth_token'][0],
            'This token is invalid'
        )

    def test_twitter_auth_token(self):
        """Test for invalid twitter token"""
        response = self.client.post(
            '/api/v1/social/auth/twitter/',
            INVALID_TWITTER_TOKENS,
            format='json'
        )
        self.assertEqual(
            response.data['errors']['auth_token'][0],
            'This token is invalid'
        )

    def test_google_verification_receives_configured_audience(self):
        """The verifier must be given our OAuth client ID as the audience"""
        from django.conf import settings
        seen = {}

        class MockGoogleAuth:

            @classmethod
            def verify_oauth2_token(cls, token, request, audience=None):
                seen['audience'] = audience
                return {
                    'iss': 'accounts.google.com',
                    'email': 'audience@email.com',
                    'name': 'audiencename',
                    'sub': '117589369073046072597'
                }

        with patch('authors.apps.social_auth.google_auth.id_token', new_callable=MockGoogleAuth):
            self.client.post(
                '/api/v1/social/auth/google/', INVALID_GOOGLE_TOKEN, format='json')
        self.assertEqual(seen['audience'], settings.GOOGLE_CLIENT_ID)

    def test_google_token_with_wrong_audience_is_rejected(self):
        """A token issued to a different app must not authenticate"""

        class MockGoogleAuth:

            @classmethod
            def verify_oauth2_token(cls, token, request, audience=None):
                raise ValueError('Token has wrong audience.')

        with patch('authors.apps.social_auth.google_auth.id_token', new_callable=MockGoogleAuth):
            response = self.client.post(
                '/api/v1/social/auth/google/', INVALID_GOOGLE_TOKEN, format='json')
        self.assertEqual(
            response.data['errors']['auth_token'][0],
            'This token is invalid'
        )

    def test_valid_google_token(self):
        """Tests for successful registration using Google social auth"""
        response = self.google_login()
        self.assertEqual(
            response.data['auth_token']['email'], 'test@email.com')
        self.assertIn('token', response.data['auth_token'])

    def test_social_user_has_no_password_and_a_social_account(self):
        """Social signup must create a SocialAccount and no credential row"""
        self.google_login()
        user = User.objects.get(email='test@email.com')
        self.assertFalse(UserPassword.objects.filter(user=user).exists())
        self.assertFalse(user.has_usable_password())
        self.assertTrue(user.is_social)
        self.assertTrue(
            SocialAccount.objects.filter(
                user=user,
                provider='google',
                provider_user_id='117589369073046072597'
            ).exists()
        )

    def test_returning_social_login_reuses_the_same_account(self):
        """A second Google login with the same sub must not create a user"""
        self.google_login()
        response = self.google_login()
        self.assertEqual(
            response.data['auth_token']['email'], 'test@email.com')
        self.assertEqual(User.objects.filter(email='test@email.com').count(), 1)
        self.assertEqual(SocialAccount.objects.count(), 1)

    def test_social_login_links_to_existing_email_account(self):
        """Google login with a known email attaches to that account"""
        self.create_user(VALID_USER_DATA_FOR_USER)
        response = self.google_login(email='anyatibrian@glo.com',
                                     name='anyatijudee')
        self.assertEqual(
            response.data['auth_token']['email'], 'anyatibrian@glo.com')
        # linked, not duplicated: same user, keeps original username & password
        user = User.objects.get(email='anyatibrian@glo.com')
        self.assertEqual(
            response.data['auth_token']['username'], 'anyatijude')
        self.assertTrue(user.is_social)
        self.assertTrue(user.has_usable_password())

    def test_password_login_rejected_for_social_only_account(self):
        """A social-only user cannot log in with a password"""
        self.google_login()
        response = self.client.post(
            self.login_url,
            data={'user': {'email': 'test@email.com', 'password': 'Whatever@123'}},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'social sign-in',
            str(response.data['errors']['error'][0])
        )

    def test_password_reset_refused_for_social_only_account(self):
        """There is no password to reset on a social-only account"""
        self.google_login()
        response = self.client.post(
            reverse('password-email'),
            data={'email': 'test@email.com'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_username_collision_gets_a_unique_username(self):
        """A social signup with a taken username must not crash"""
        self.create_user(VALID_USER_DATA_FOR_USER)
        response = self.google_login(email='other@email.com',
                                     name='anyatijude')
        self.assertEqual(
            response.data['auth_token']['email'], 'other@email.com')
        self.assertNotEqual(
            response.data['auth_token']['username'], 'anyatijude')

    def test_no_email_address_in_user_data(self):
        """Tests for their being no email address in decoded token information"""

        class MockGoogleAuth:

            @classmethod
            def verify_oauth2_token(cls, token, request, audience=None):
                """Method Returns dummy google user decoded info"""
                return {
                    'iss': 'accounts.google.com',
                    'name': 'testname',
                    'sub': '117589369073046072597'
                }

        with patch('authors.apps.social_auth.google_auth.id_token', new_callable=MockGoogleAuth):
            response = self.client.post(
                '/api/v1/social/auth/google/', INVALID_GOOGLE_TOKEN, format='json')
            self.assertEqual(
                response.data['auth_token'], "Email address not provided!")

    def test_valid_facebook_token(self):
        """Tests for successful registration using facebook social auth"""

        class MockFacebookAuth:

            @classmethod
            def request(cls, auth_token):
                """Method returns dummy facebook user decoded info"""
                return {
                    'email': 'facebook@email.com',
                    'name': 'facebookname',
                    'id': '23434343',
                    'picture': 'https://gooaus/23434klk3'
                }

            def __call__(self, *args, **kwargs):
                return self

        with patch('authors.apps.social_auth.facebook_auth.facebook.GraphAPI', new_callable=MockFacebookAuth):
            response = self.client.post(
                '/api/v1/social/auth/facebook/', INVALID_FACEBOOK_TOKEN, format='json')
            self.assertEqual(
                response.data['auth_token']['email'], "facebook@email.com")
            self.assertTrue(
                SocialAccount.objects.filter(
                    provider='facebook', provider_user_id='23434343'
                ).exists()
            )

    def test_facebook_token_with_picture_dict(self):
        """Facebook token with nested dict for picture resolves correctly"""
        class MockFacebookAuthDict:
            @classmethod
            def request(cls, auth_token):
                return {
                    'email': 'fbdict@email.com',
                    'name': 'Facebook Dict User',
                    'id': '99881122',
                    'picture': {'data': {'url': 'https://example.com/fbdict.jpg'}}
                }

            def __call__(self, *args, **kwargs):
                return self

        with patch('authors.apps.social_auth.facebook_auth.facebook.GraphAPI', new_callable=MockFacebookAuthDict):
            response = self.client.post(
                '/api/v1/social/auth/facebook/', INVALID_FACEBOOK_TOKEN, format='json')
            self.assertEqual(response.status_code, 200)
            user = User.objects.get(email='fbdict@email.com')
            self.assertEqual(user.profile.full_name, 'Facebook Dict User')
            self.assertEqual(user.profile.image, 'https://example.com/fbdict.jpg')

    def test_social_registration_with_empty_email_field(self):
        """Tests for data from decoded token containing no email address"""
        response = register_social_user(
            provider='google',
            provider_user_id=EMPTY_SOCIAL_EMAIL_DATA['id'],
            email=EMPTY_SOCIAL_EMAIL_DATA['email'],
            username=EMPTY_SOCIAL_EMAIL_DATA['username']
        )
        self.assertEqual(response, 'Empty email address')

    def test_successful_social_registration(self):
        """Tests for successful registration on the app using social authentication"""
        response = register_social_user(
            provider='google',
            provider_user_id=VALID_SOCIAL_DATA['id'],
            email=VALID_SOCIAL_DATA['email'],
            username=VALID_SOCIAL_DATA['username'],
            full_name='Patrick Fitz',
            image='https://example.com/pfitz.jpg'
        )
        self.assertEqual(response['email'], 'test@email.com')
        self.assertIn('token', response)
        user = User.objects.get(email='test@email.com')
        self.assertEqual(user.profile.full_name, 'Patrick Fitz')
        self.assertEqual(user.profile.image, 'https://example.com/pfitz.jpg')

    def test_social_sync_via_google_endpoint(self):
        """Google login populates full_name and image on user profile"""
        class MockGoogleAuth:
            @classmethod
            def verify_oauth2_token(cls, token, request, audience=None):
                return {
                    'iss': 'accounts.google.com',
                    'email': 'gprofile@email.com',
                    'name': 'Google Fullname',
                    'picture': 'https://example.com/google-pic.jpg',
                    'sub': '9988776655'
                }

        with patch('authors.apps.social_auth.google_auth.id_token', new_callable=MockGoogleAuth):
            response = self.client.post('/api/v1/social/auth/google/', INVALID_GOOGLE_TOKEN, format='json')
            self.assertEqual(response.status_code, 200)
            user = User.objects.get(email='gprofile@email.com')
            self.assertEqual(user.profile.full_name, 'Google Fullname')
            self.assertEqual(user.profile.image, 'https://example.com/google-pic.jpg')
