import json
from django.test import TestCase
from authors.apps.authentication.models import User
from rest_framework.test import (APIClient, APITestCase)
from django.urls import reverse
from authors.apps.profiles.tests.test_data import (
    VALID_LOGIN_DATA, VALID_USER_DATA)


class BaseTestProfile(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register-user')
        self.login_url = reverse('login-user')
        self.profile_url = reverse('user-profiles')
        self.user_list_url = reverse('users-list')
        response = self.client.post(self.register_url,
                                    content_type='application/json',
                                    data=json.dumps(VALID_USER_DATA)
                                    )
        self.activate_email = reverse('activate-user',
                                      kwargs={'token': response.data['token']}
                                      )
        self.client.get(
            self.activate_email
        )
        login_response = self.client.post(self.login_url,
                                          content_type='application/json',
                                          data=json.dumps(VALID_LOGIN_DATA)
                                          )
        self.user_token = login_response.data['token']
