import json
from rest_framework.test import APIClient, APITestCase
from .base import BaseTest
from rest_framework import status, response
from django.urls import reverse
from .base import ArticlesBaseTest
from .test_data import (
    VALID_ARTICLE, 
    VALID_COMMENT,
    VALID_COMMENT_2
)
from authors.apps.authentication.tests.test_data import (
    VALID_USER_DATA,
    VALID_LOGIN_DATA,
)
from authors.apps.profiles.tests.test_data import VALID_USER_DATA_2


class CommentCreateTest(ArticlesBaseTest):
    """
    Test Commentin on articles
    """

    def test_user_can_comment_on_article_data(self):
        """
        User can create comment
        """
        token1 = self.create_user(VALID_USER_DATA)
        response = self.create_article(VALID_ARTICLE, token1)
        response = self.create_comment(
            token=token1, 
            parentId=0,
            slug=response.data['article']['slug']
        )

        self.assertEqual(
            response.data['comment']['body'], 
            VALID_COMMENT['body']
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )


    def test_user_can_get_a_comment(self):
        """
        User can get a comment
        """
        token1 = self.create_user(VALID_USER_DATA)
        response = self.create_article(VALID_ARTICLE, token1)
        response = self.create_comment(
            token=token1, 
            parentId=0,
            slug=response.data['article']['slug']
        )
        get_comment_url = reverse('crud-comment', kwargs={
            'id': response.data['comment']['id']
        })
        response = self.client.get(
            get_comment_url
        )
        self.assertEqual(
            response.data['body'], 
            VALID_COMMENT['body']
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )


    def test_user_can_reply_to_comment(self):
        """
        User can reply to a comment
        """
        token1 = self.create_user(VALID_USER_DATA)
        response = self.create_article(VALID_ARTICLE, token1)
        response = self.create_comment(
            token=token1, 
            parentId=0,
            slug=response.data['article']['slug']
        )
        response = self.create_comment(
            token=token1, 
            parentId=response.data['comment']['id'],
            slug=response.data['comment']['article']['slug']
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )
        self.assertEqual(
            response.data['comment']['body'],
            VALID_COMMENT['body']
        )


    def test_user_can_get_comments_for_an_article(self):
        """
        user can get comments for an article
        """
        token1 = self.create_user(VALID_USER_DATA)
        response = self.create_article(VALID_ARTICLE, token1)
        response = self.create_comment(
            token=token1, 
            parentId=0,
            slug=response.data['article']['slug']
        )
        get_comment_url = reverse('comments', kwargs={
            'slug': response.data['comment']['article']['slug'],
            'id': 0
        })
        response = self.client.get(
            get_comment_url
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )


    def test_user_can_delete_their_comment(self):
        """
        user can delete comments for an article
        """
        token = self.create_user(VALID_USER_DATA)
        response = self.create_article(VALID_ARTICLE, token)
        response = self.create_comment(
            token=token,
            parentId=0,
            slug=response.data['article']['slug']
        )
        get_comment_url = reverse('crud-comment', kwargs={
            'id': response.data['comment']['id']
        })
        response = self.client.delete(
            get_comment_url,
            HTTP_AUTHORIZATION=token
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )



    def test_invalid_user_can_delete_a_comment(self):
        """
        user can delete comments for an article
        """
        token = self.create_user(VALID_USER_DATA)
        response = self.create_article(VALID_ARTICLE, token)
        response = self.create_comment(
            token=token,
            parentId=0,
            slug=response.data['article']['slug']
        )
        token = self.create_user(VALID_USER_DATA_2)
        get_comment_url = reverse('crud-comment', kwargs={
            'id': response.data['comment']['id']
        })
        response = self.client.delete(
            get_comment_url,
            HTTP_AUTHORIZATION=token
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )


    def test_user_can_update_their_comment(self):
        """
        user can delete comments for an article
        """
        token = self.create_user(VALID_USER_DATA)
        response = self.create_article(VALID_ARTICLE, token)

        response = self.create_comment(
            token=token,
            parentId=0,
            slug=response.data['article']['slug']
        )
        get_comment_url = reverse('crud-comment', kwargs={
            'id': response.data['comment']['id']
        })
        response = self.client.put(
            get_comment_url,
            HTTP_AUTHORIZATION=token,
            data=VALID_COMMENT_2,
            format='json'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )


    def test_invalid_user_can_update_comment(self):
        """
        invalid user can delete comments for an article
        """
        token = self.create_user(VALID_USER_DATA)
        response = self.create_article(VALID_ARTICLE, token)

        response = self.create_comment(
            token=token,
            parentId=0,
            slug=response.data['article']['slug']
        )
        token = self.create_user(VALID_USER_DATA_2)

        get_comment_url = reverse('crud-comment', kwargs={
            'id': response.data['comment']['id']
        })
        response = self.client.put(
            get_comment_url,
            HTTP_AUTHORIZATION=token,
            data=VALID_COMMENT_2,
            format='json'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )