from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from authors.apps.authentication.models import User
from authors.apps.authentication.tests.test_data import VALID_LOGIN_DATA, VALID_USER_DATA
from authors.apps.authentication.tests.base import BaseTest
from authors.apps.articles.tests.test_data import VALID_COMMENT, VALID_ARTICLE, VALID_ARTICLE_4


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

    def create_comment(self, token, slug, parentId):
        

        create_comment_url = reverse('comments', kwargs={
            'slug': slug,
            'id': int(parentId)
            }
        )

        return self.client.post(
            create_comment_url,
            HTTP_AUTHORIZATION=token,
            data=VALID_COMMENT,
            format='json'
        )