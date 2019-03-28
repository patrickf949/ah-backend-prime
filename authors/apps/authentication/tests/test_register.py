from rest_framework import status
from .base import BaseTest
from django.urls import reverse
from .test_data import (
                        valid_user_data,
                        empty_email, 
                        empty_username, 
                        empty_password,invalid_email
                        )



class UserRegisterTest(BaseTest):
    """
    contains user login tests method
    """
    def test_register_user(self):
        """
        test user registration valid credentialsß

        """
        self.response = self.client.post(
            reverse('register-user'),
            data= valid_user_data,
            format='json'
        )
        self.assertEquals(self.response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(self.response.data["username"],"anyatijude")
        self.assertEquals(self.response.data["email"],"anyatijude@glo.com")
    
    def test_empty_username(self):
        """ 
        test user registration without username

        """
        self.response = self.client.post(
            reverse('register-user'),
            data= empty_username,
            format='json'
        )
        self.assertEquals(self.response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(self.response.data["errors"]["username"][0],"This field may not be blank.")
    
    def test_empty_email(self):
        """ 
        test user registration without email

        """
        self.response = self.client.post(
            reverse('register-user'),
            data= empty_email,
            format='json'
        )
        self.assertEquals(self.response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(self.response.data["errors"]["email"][0],"This field may not be blank.")
    
    def test_empty_password(self):
        """
        test user registration without password

        """


        self.response = self.client.post(
            reverse('register-user'),
            data= empty_password,
            format='json'
        )
        self.assertEquals(self.response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(self.response.data["errors"]["password"][0],"This field may not be blank.")
    
    def test_empty_invalide_email(self):
        """ 
        test user registration with invalid email

        """
        self.response = self.client.post(
            reverse('register-user'),
            data= invalid_email,
            format='json'
        )
        self.assertEquals(self.response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(self.response.data["errors"]["email"][0],"Enter a valid email address.")
        
        