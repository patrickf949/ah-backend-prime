import os
import jwt
from datetime import datetime,timedelta
from django.urls import reverse
from rest_framework import status
from authors.apps.authentication.models import User
from authors.apps.authentication.tests.base import BaseTest
from authors.settings import SECRET_KEY
from authors.apps.authentication.tests.test_data import EMAIL_ACTIVATION_DATA,PASSWORD_RESET_DATA,VALID_USER_DATA


class TestPasswordTest(BaseTest):
    """
    test for password reset and
    send password reset token during account reset

    """

    def test_send_email_activation_link(self):
        """
        test to send invalide email during
        password reset

        """
        response = self.client.post(
            self.register_url,
            data=VALID_USER_DATA,
            format='json'
        )
        response = self.client.post(
            self.passoword_reset_url,
            data=EMAIL_ACTIVATION_DATA,
            format='json'
        )

        self.assertEquals(
            response.status_code,
             status.HTTP_200_OK
             )

        self.assertEquals(
            response.data['message'],
            'password reset link has been sent to your email'
            )

    def test_email_does_not_exist_during_send_token(self):
        """
        test to check invalid email during password
        process

        """
        self.response = self.client.post(
            self.passoword_reset_url,
            data=EMAIL_ACTIVATION_DATA,
            format='json'
        )

        self.assertEquals(
            self.response.status_code,
            status.HTTP_400_BAD_REQUEST
                          )

        self.assertEquals(
            self.response.data['error'],
            'the email does not match any account'
            )

    def test_password_reset(self):
        """
        test to ensure that the user
        is able to change his or her password

        """
        token_bearer =self.create_user(VALID_USER_DATA)
        list = token_bearer.split()
        token =list[1]
        self.response = self.client.put(
            reverse('password-reset', kwargs={'token': token}),
            data={
                "user": {
                    "password": "0781901036",
                    "confirmpassword": "0781901036"
                }

            },
            format='json'
        )
        self.assertEquals(self.response.status_code, status.HTTP_200_OK)
        self.assertEquals(
            self.response.data['message'],
            'your password has been reset successfully'
            )

    def test_password_not_match_at_reset(self):
        """
        test for incase the user enters
        passwords which do not match

        """
        token_bearer =self.create_user(VALID_USER_DATA)
        list = token_bearer.split()
        token =list[1]
        self.response = self.client.put(
            reverse('password-reset', kwargs={'token': token}
            ),
            data={
                "user": {
                    "password": "0781901036",
                    "confirmpassword": "078190"
                }

            },
            format='json'
        )
        self.assertEquals(
            self.response.status_code,
            status.HTTP_400_BAD_REQUEST
            )
        self.assertEquals(
            self.response.data['error'],
            'password and confirm password fields do not match'
            )

    def test_short_password_length_at_reset(self):
        token_bearer =self.create_user(VALID_USER_DATA)
        list = token_bearer.split()
        token =list[1]
        self.response = self.client.put(
            reverse('password-reset', kwargs={'token': token}),
            data={
                "user": {
                    "password": "078",
                    "confirmpassword": "078"
                }

            },
            format='json'
        )

        self.assertEquals(
            self.response.status_code,
            status.HTTP_400_BAD_REQUEST
                          )
