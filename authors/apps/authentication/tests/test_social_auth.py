from rest_framework import status
from django.urls import reverse
from .base import BaseTest
from unittest.mock import patch
from authors.apps.social_auth.register import register_user
from .test_data import (
    INVALID_GOOGLE_TOKEN,
    INVALID_FACEBOOK_TOKEN,
    INVALID_GOOGLE_TOKEN,
    INVALID_TWITTER_TOKENS,
    VALID_USER_DATA,
    NO_SOCIAL_EMAIL_DATA,
    EMPTY_SOCIAL_EMAIL_DATA,
    VALID_SOCIAL_DATA
)



class SocialAuthRegistration(BaseTest):
    """
    contains tests for  social auth registration
    """


    def test_google_invalid_token(self):
        '''Test for invalid google token'''
        response = self.client.post(
            '/api/social/auth/google/',
            INVALID_GOOGLE_TOKEN,
            format='json'
        )
        self.assertEqual(
            response.data['errors']['auth_token'][0],
            'This token is invalid'
        )

    def test_facebook_invalid_token(self):
        '''Test for invalid facebook token'''
        response = self.client.post(
            '/api/social/auth/facebook/',
            INVALID_FACEBOOK_TOKEN,
            format='json'
        )
        self.assertEqual(
            response.data['errors']['auth_token'][0],
            'This token is invalid'
        )

    def test_twitter_auth_token(self):
        '''Test for invalid twitter token'''
        response = self.client.post(
            '/api/social/auth/twitter/',
            INVALID_TWITTER_TOKENS,
            format='json'
        )
        self.assertEqual(
            response.data['errors']['auth_token'][0],
            'This token is invalid'
        )


    def test_valid_google_token(self):
        ''''Tests for successful registration using Google social auth'''

        class MockGoogleAuth:

            @classmethod
            def verify_oauth2_token(cls, token, request):
                '''Method Returns dummy google user decoded info'''
                return {
                    'iss': 'accounts.google.com',
                    'email': 'test@email.com',
                    'name': 'testname',
                    'sub': '117589369073046072597'
                }

        with patch('authors.apps.social_auth.google_auth.id_token', new_callable=MockGoogleAuth):
            response = self.client.post('/api/social/auth/google/', INVALID_GOOGLE_TOKEN, format='json')
            self.assertEqual(response.data['auth_token'], "{'email': 'test@email.com', 'username': 'testname', 'token': <bound method User.generated_jwt_token of <User: test@email.com>>}")


    def test_valid_facebook_token(self):
        ''''Tests for successful registration using facebook social auth'''

        class MockFacebookAuth:


            @classmethod
            def request(cls, auth_token):
                ''''Method returns dummy facebook user decoded info'''
                return {
                    'email': 'facebook@email.com',
                    'name': 'facebookname',
                    'id': '23434343',
                    'picture': 'https://gooaus/23434klk3'
                }

            def __call__(self, *args, **kwargs):
                return self

        with patch('authors.apps.social_auth.facebook_auth.facebook.GraphAPI', new_callable=MockFacebookAuth):
            response = self.client.post('/api/social/auth/facebook/', INVALID_FACEBOOK_TOKEN, format='json')
            self.assertEqual(response.data['auth_token'], "{'email': 'facebook@email.com', 'username': 'facebookname', 'token': <bound method User.generated_jwt_token of <User: facebook@email.com>>}") 


    def test_no_email_address_in_user_data(self):
        '''Tests for their being no email address in decoded token information'''

        class MockGoogleAuth:

            @classmethod
            def verify_oauth2_token(cls, token, request):
                '''Method Returns dummy google user decoded info'''
                return {
                    'iss': 'accounts.google.com',
                    'name': 'testname',
                    'sub': '117589369073046072597'
                }

        with patch('authors.apps.social_auth.google_auth.id_token', new_callable=MockGoogleAuth):
            response = self.client.post('/api/social/auth/google/', INVALID_GOOGLE_TOKEN, format='json')
            self.assertEqual(response.data['auth_token'], "Email address not provided!")

    def test_social_registration_with_existing_user(self):
        '''Tests for registering a user using social auth that already exists in app DB'''
        self.create_user(VALID_USER_DATA)
        response = register_user(VALID_USER_DATA['user']['email'], 'username')
        self.assertEqual(response, 'This email address already exists! Please log in!')


    def test_social_registration_with_empty_email_field(self):
        '''Tests for data from decoded token containing no email address'''
        email = EMPTY_SOCIAL_EMAIL_DATA['email']
        username = EMPTY_SOCIAL_EMAIL_DATA['username']
        response = register_user(email, username)
        self.assertEqual(response, 'Empty email address')

    def test_successful_social_registration(self):
        '''Tests for successful registration on the app using social authentication'''
        email = VALID_SOCIAL_DATA['email']
        username = VALID_SOCIAL_DATA['username']
        response = register_user(email, username)
        self.assertEqual(response["email"], "test@email.com")
