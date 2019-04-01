import jwt
import os
from rest_framework.test import APIClient,APITestCase
from .base import BaseTest
from rest_framework import status
from django.urls import reverse
from .test_data import ( 
    VALID_LOGIN_DATA, 
    VALID_USER_DATA, 
    LOGIN_RESPONSE,
    EMPTY_LOGIN_EMAIL, 
    EMPTY_LOGIN_PASSWORD
    )


class LoginUserTest(BaseTest):
    """
    test userlogin with correct credentials
    """

    def test_user_login(self):
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
        self.assertEquals(response.data['email'],
        'anyatibrian@glo.com')
    
    def test_invalide_user_login(self):
        """
         test user login with invalide credentials

        """
        response = self.client.post(
            self.login_url,
            data=VALID_LOGIN_DATA,
            format='json'
        )
        self.assertEquals(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEquals(
            response.data['errors']['error'][0],
            "A user with this email and password was not found."
        )

    def test_empty_login(self):
        """
        test user login without email

        """
        response = self.client.post(
            self.login_url,
            data=EMPTY_LOGIN_EMAIL,
            format='json'
        )
        self.assertEquals(
            response.status_code, 
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEquals(
            response.data['errors']['email'][0], 
            "This field may not be blank."
        )
    
    def test_empty_password(self):
        """
        test user login without password
        """
        response = self.client.post(
            self.login_url,
            data=EMPTY_LOGIN_PASSWORD,
            format='json'
        )
        self.assertEquals(
            response.status_code, 
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEquals(
            response.data['errors']['password'][0], 
            "This field may not be blank."
        )

    
    def test_get_user(self):
        """
        test to get the current logged in user
        """
        token = self.create_user(VALID_USER_DATA)

        response = self.client.get('/api/user/', HTTP_AUTHORIZATION=token, format='json')
        response = self.client.get(self.users, HTTP_AUTHORIZATION=token, format='json')
        self.assertEqual(response.data["email"], VALID_USER_DATA.get('user').get('email'))
        self.assertEqual(response.data["username"], VALID_USER_DATA.get('user').get('username'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
