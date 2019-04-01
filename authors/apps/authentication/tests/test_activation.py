from rest_framework.test import APIClient,APITestCase
from .base import BaseTest
from rest_framework import status
from django.urls import reverse
from .test_data import ( 
    VALID_USER_DATA,
    VALID_LOGIN_DATA,
    ERROR_LOGIN
    )


class ActivateUserTest(BaseTest):
    """
    Test Activation of users
    """
    
    def test_activated_user_can_login(self):
        """
        activated user can login
        """
        self.create_user(VALID_USER_DATA)
        response = self.client.post(
            self.login_url,
            data=VALID_LOGIN_DATA,
            format='json'
        )
        self.assertEquals(
            response.status_code , 
            status.HTTP_200_OK
        )
        self.assertEquals(
            response.data['email'],
            'anyatibrian@glo.com'
        )
    

    def test_non_activated_user_login(self):
        """
        non activated user login
        """
        response = self.client.post(
            self.register_url,
            data=VALID_LOGIN_DATA,
            format='json'
        )

        response = self.client.post(
            self.login_url,
            data=VALID_LOGIN_DATA,
            format='json'
        )
        self.assertEquals(
            response.status_code , 
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEquals(
            response.data,
            ERROR_LOGIN
        )

