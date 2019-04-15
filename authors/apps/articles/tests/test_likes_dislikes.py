import json
from rest_framework import status, response
from django.urls import reverse
from .base import ArticlesBaseTest
from .test_data import VALID_ARTICLE
from authors.apps.authentication.tests.test_data import (
    VALID_USER_DATA
)
from rest_framework.test import APIClient, APITestCase
from .base import BaseTest



class TestLikeDislikeArticle(ArticlesBaseTest):
    '''Test likes and dislikes functionality'''


    def test_like_article(self):
        '''Test for liking article'''
        token = self.create_user(VALID_USER_DATA)
        response = self.client.post(
            self.create_articles,
            HTTP_AUTHORIZATION=token,
            data=VALID_ARTICLE,
            format='json'
        )
        articles_slug = response.data['article']['slug']
        response = self.client.post(
            f'/api/v1/articles/{articles_slug}/like/',
            HTTP_AUTHORIZATION=token
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['likes'], 1)


    def test_dislike_article(self):
        '''Test for disliking article'''
        token = self.create_user(VALID_USER_DATA)
        response = self.client.post(
            self.create_articles,
            HTTP_AUTHORIZATION=token,
            data=VALID_ARTICLE,
            format='json'
        )
        articles_slug = response.data['article']['slug']
        response = self.client.post(
            f'/api/v1/articles/{articles_slug}/dislike/',
            HTTP_AUTHORIZATION=token
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['dislikes'], 1)


    def test_like_article_twice(self):
        '''Test for disliking article twice'''
        token = self.create_user(VALID_USER_DATA)
        response = self.client.post(
            self.create_articles,
            HTTP_AUTHORIZATION=token,
            data=VALID_ARTICLE,
            format='json'
        )
        articles_slug = response.data['article']['slug']
        self.client.post(
            f'/api/v1/articles/{articles_slug}/like/',
            HTTP_AUTHORIZATION=token
        )
        response = self.client.post(
            f'/api/v1/articles/{articles_slug}/like/',
            HTTP_AUTHORIZATION=token
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['likes'], 0)


    def test_dislike_article_twice(self):
        '''Test for disliking article twice'''
        token = self.create_user(VALID_USER_DATA)
        response = self.client.post(
            self.create_articles,
            HTTP_AUTHORIZATION=token,
            data=VALID_ARTICLE,
            format='json'
        )
        articles_slug = response.data['article']['slug']
        self.client.post(
            f'/api/v1/articles/{articles_slug}/dislike/',
            HTTP_AUTHORIZATION=token
        )
        response = self.client.post(
            f'/api/v1/articles/{articles_slug}/dislike/',
            HTTP_AUTHORIZATION=token
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['dislikes'], 0)


    def test_like_disliked_article_twice(self):
        '''Test for liking a disliked article'''
        token = self.create_user(VALID_USER_DATA)
        response = self.client.post(
            self.create_articles,
            HTTP_AUTHORIZATION=token,
            data=VALID_ARTICLE,
            format='json'
        )
        articles_slug = response.data['article']['slug']
        self.client.post(
            f'/api/v1/articles/{articles_slug}/like/',
            HTTP_AUTHORIZATION=token
        )
        response = self.client.post(
            f'/api/v1/articles/{articles_slug}/dislike/',
            HTTP_AUTHORIZATION=token
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['likes'], 0)
        self.assertEqual(response.data['dislikes'], 1)
