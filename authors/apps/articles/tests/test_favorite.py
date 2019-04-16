import json
from rest_framework.test import APIClient, APITestCase
from .base import BaseTest
from rest_framework import status, response
from django.urls import reverse
from .base import ArticlesBaseTest
from .test_data import (
    VALID_ARTICLE,
)
from authors.apps.authentication.tests.test_data import (
    VALID_USER_DATA,
    VALID_LOGIN_DATA,
)
from authors.apps.profiles.tests.test_data import VALID_USER_DATA_2


class ArticleFavorite(ArticlesBaseTest):
    """
    Tests for ArticleFavoritin
    """
    def test_user_can_favorite_an_article(self):
        """
        user can favorite an article
        """
        token = self.create_user(VALID_USER_DATA)
        response = self.create_article(VALID_ARTICLE, token)
        favorite_comment_url = reverse(
            'favorite-article', 
            kwargs={'slug': response.data['article']['slug']}
        )
        response = self.client.post(
            favorite_comment_url,
            HTTP_AUTHORIZATION=token
        )
        self.assertIn(
            'You have favorited',
            response.data['message']            
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )


    def test_user_can_favorite_an_article_twice(self):
        """
        user can favorite an article twice
        """
        token = self.create_user(VALID_USER_DATA)
        response = self.create_article(VALID_ARTICLE, token)
 
        favorite_comment_url = reverse(
            'favorite-article', 
            kwargs={'slug': response.data['article']['slug']}
        )
        response = self.client.post(
            favorite_comment_url,
            HTTP_AUTHORIZATION=token
        )
        response = self.client.post(
            favorite_comment_url,
            HTTP_AUTHORIZATION=token
        )
        self.assertIn(
            'You already favorited',
            response.data['message']            
        )


    def test_user_can_unfavorite_an_article(self):
        """
        user can unfavorite an article
        """
        token = self.create_user(VALID_USER_DATA)
        response = self.create_article(VALID_ARTICLE, token)
        slug = response.data['article']['slug']
        favorite_comment_url = reverse(
            'favorite-article', 
            kwargs={'slug': slug}
        )
        response = self.client.post(
            favorite_comment_url,
            HTTP_AUTHORIZATION=token
        )
        unfavorite_comment_url = reverse(
            'unfavorite-article', 
            kwargs={'slug': slug}
        )
        response = self.client.delete(
            unfavorite_comment_url,
            HTTP_AUTHORIZATION=token
        )
        self.assertIn(
            'You have unfavorited',
            response.data['message']            
        )


    def test_user_can_get_users_who_favorited_article(self):
        """
        user can get all users who favorited an article
        """
        token = self.create_user(VALID_USER_DATA)
        response = self.create_article(VALID_ARTICLE, token)
        slug = response.data['article']['slug']
        favorite_comment_url = reverse(
            'favorite-article', 
            kwargs={'slug': slug}
        )
        response = self.client.post(
            favorite_comment_url,
            HTTP_AUTHORIZATION=token
        )
        get_users_who_favorited_url = reverse(
            'favorite-article', 
            kwargs={'slug': slug}
        )
        response = self.client.get(
            get_users_who_favorited_url,
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK            
        )


    def test_unfavorite_an_article_without_favoriting(self):
        """
        Unfavorite an article without having favorited it before
        """
        token = self.create_user(VALID_USER_DATA)
        response = self.create_article(VALID_ARTICLE, token)
        slug = response.data['article']['slug']
        unfavorite_comment_url = reverse(
            'unfavorite-article', 
            kwargs={'slug': slug}
        )
        response = self.client.delete(
            unfavorite_comment_url,
            HTTP_AUTHORIZATION=token
        )
        self.assertIn(
            'You have never favorited',
            response.data['message']            
        )