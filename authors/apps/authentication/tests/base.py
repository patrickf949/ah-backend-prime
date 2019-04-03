from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from authors.apps.authentication.models import User
from authors.apps.authentication.tests.test_data import VALID_LOGIN_DATA, VALID_USER_DATA


class BaseTest(APITestCase):
    """
    sets up a base class upon which all our test depends on
    """
    def setUp(self):
        self.client= APIClient()
        self.register_url = reverse('register-user')
        self.login_url = reverse('login-user')
        self.args = ''

    def _generate_jwt_token(self):

        if not BaseTest.token:
            self.client.post(self.register_url, VALID_USER_DATA, format='json')
            response = self.client.post(self.login_url, VALID_LOGIN_DATA, format='json')

            BaseTest.token = response.data["token"]
        return BaseTest.token


    def create_user(self, datan):
        response = self.client.post(self.register_url, datan, format='json')
        self.activate_email = reverse('activate-user',kwargs={
            'token':response.data['token']
        })
        self.client.get(
            self.activate_email
        )
        response = self.client.post(self.login_url, datan, format='json')
        
        return f'Bearer {response.data["token"]}'
        
        
    
