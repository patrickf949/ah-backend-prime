from rest_framework.test import APIClient,APITestCase
from django.urls import reverse
from ...authentication.models import User


class BaseTest(APITestCase):
    """
    sets up a base class upon which all our test depends on
    """
    def setUp(self):
        self.client= APIClient()
        self.register_url = reverse('register-user')
        self.login_url = reverse('login-user')
        
    
