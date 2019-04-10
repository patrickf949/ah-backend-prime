import json
from rest_framework.test import APIClient,APITestCase
from .base import BaseTest
from rest_framework import status, response
from django.urls import reverse
from .base import ArticlesBaseTest
from .test_data import VALID_ARTICLE, INVALID_ARTICLE, VALID_UPDATE_ARTICLE
from authors.apps.authentication.tests.test_data import ( 
    VALID_USER_DATA,
    VALID_LOGIN_DATA,
    )
from authors.apps.profiles.tests.test_data import VALID_USER_DATA_2

class ArticleCreateTest(ArticlesBaseTest):
    """
    Test Activation of users
    """
    
    def test_user_can_create_article_with_valid_data(self):
        """
        User can create article
        """
        token = self.create_user(VALID_USER_DATA)
        response = self.client.post(
            self.create_articles,
            HTTP_AUTHORIZATION=token,
            data=VALID_ARTICLE,
            format='json'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )
        
    

    def test_create_article_invalid_data(self):
        """
        test if a user can Create article with invalid data
        """
        token = self.create_user(VALID_USER_DATA)
        response = self.client.post(
            self.create_articles,
            HTTP_AUTHORIZATION=token,
            data=INVALID_ARTICLE,
            format='json'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )


    def test_update_article_valid_user(self):
        """
        test if author can update article
        """
        token = self.create_user(VALID_USER_DATA)
        response = self.create_article(
            token=token,
            article=VALID_ARTICLE
        )
        update_url = reverse('crud-article',kwargs={
            'slug': response.data['article']['slug']
        })
        response1 = self.client.put(
            update_url,
            data=VALID_UPDATE_ARTICLE,
            HTTP_AUTHORIZATION=token,
            format='json'
        )
        self.assertEqual(
            response1.status_code,
            status.HTTP_200_OK
        )
    
    def test_update_article_invalid_slug(self):
        """
        test if author can update non existent article
        """
        token = self.create_user(VALID_USER_DATA)
        response = self.create_article(
            token=token,
            article=VALID_ARTICLE
        )
        update_url = reverse('crud-article',kwargs={
            'slug': 'invalid-slug'
        })
        response1 = self.client.put(
            update_url,
            data=VALID_UPDATE_ARTICLE,
            HTTP_AUTHORIZATION=token,
            format='json'
        )
        self.assertEqual(
            response1.status_code,
            status.HTTP_400_BAD_REQUEST
        )
    

    def test_update_article_invalid_user(self):
        """
        test if invalid author can update article
        """
        token = self.create_user(VALID_USER_DATA)
        response = self.create_article(
            token=token,
            article=VALID_ARTICLE
        )
        token2 = self.create_user(VALID_USER_DATA_2)
        update_url = reverse('crud-article',kwargs={
            'slug': response.data['article']['slug']
        })
        response1 = self.client.put(
            update_url,
            data=VALID_UPDATE_ARTICLE,
            HTTP_AUTHORIZATION=token2,
            format='json'
        )
        self.assertEqual(
            response1.status_code,
            status.HTTP_403_FORBIDDEN
        )
    

    def test_get_one_valid_article(self):
        """
        test if user can get existent article
        """
        token = self.create_user(VALID_USER_DATA)
        response = self.create_article(
            token=token,
            article=VALID_ARTICLE
        )
        get_article_url = reverse('crud-article',kwargs={
            'slug': response.data['article']['slug']
        })
        response = self.client.get(
            get_article_url
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            response.data['article']['title'],
            VALID_ARTICLE['title']
        )
    

    def test_get_one_invalid_article(self):
        """
        test if user can get non existent article
        """
        get_article_url = reverse('crud-article',kwargs={
            'slug': 'invalid-slug'
        })
        response = self.client.get(
            get_article_url
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            response.data['message'],
            'The article does not exist'
        )


    def test_delete_one_valid_article(self):
        """
        test if valid user can delete existent article
        """
        token = self.create_user(VALID_USER_DATA)
        response = self.create_article(
            token=token,
            article=VALID_ARTICLE
        )
        get_article_url = reverse('crud-article',kwargs={
            'slug': response.data['article']['slug']
        })
        response = self.client.delete(
            get_article_url,
            HTTP_AUTHORIZATION=token
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            response.data['message'],
            "Article has been successfully deleted"
        )


    def test_delete_one_invalid_article(self):
        """
        test if valid user can delete non existent article
        """
        token = self.create_user(VALID_USER_DATA)
        response = self.create_article(
            token=token,
            article=VALID_ARTICLE
        )
        get_article_url = reverse('crud-article',kwargs={
            'slug': 'invalid-slug'
        })
        response = self.client.delete(
            get_article_url,
            HTTP_AUTHORIZATION=token
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            response.data['message'],
            "The article does not exist"
        )
    

    def test_invalid_author_deletes_article(self):
        """
        test if an invalid author can delete an article
        """
        token = self.create_user(VALID_USER_DATA)
        response = self.create_article(
            token=token,
            article=VALID_ARTICLE
        )
        get_article_url = reverse('crud-article',kwargs={
            'slug': response.data['article']['slug']
        })
        token2 = self.create_user(VALID_USER_DATA_2)
        response = self.client.delete(
            get_article_url,
            HTTP_AUTHORIZATION=token2
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )
        self.assertEqual(
            response.data['message'],
            "You do not have permissions to delete this article"
        )
        

    