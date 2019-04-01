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
    
    def _generate_jwt_token(self):

        if not BaseTest.token:
            self.client.post(self.register_url, VALID_USER_DATA, format='json')
            response = self.client.post(self.login_url, VALID_LOGIN_DATA, format='json')

            BaseTest.token = response.data["token"]
        return BaseTest.token

    def create_user(self, data):
        self.client.post(self.register_url, data, format='json')
        response = self.client.post(self.login_url, data, format='json')

        return f'Bearer {response.data["token"]}'
        
    
