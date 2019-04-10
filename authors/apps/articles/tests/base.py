from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from authors.apps.authentication.models import User
from authors.apps.authentication.tests.test_data import VALID_LOGIN_DATA, VALID_USER_DATA
from authors.apps.authentication.tests.base import BaseTest


class ArticlesBaseTest(BaseTest):
    """
    sets up a base class upon which all our test depends on
    """

    def setUp(self):
        super().setUp()
        self.create_articles = reverse('articles')

    def create_article(self, article, token):
        return self.client.post(
            self.create_articles,
            data=article,
            HTTP_AUTHORIZATION=token,
            format='json'
        )