import json
from rest_framework.test import APIClient, APITestCase
from .base import BaseTest
from rest_framework import status, response
from django.urls import reverse
from .base import ArticlesBaseTest
from .test_data import (VALID_ARTICLE, 
                        INVALID_ARTICLE, 
                        VALID_UPDATE_ARTICLE, 
                        VALID_ARTICLE_2, 
                        INVALID_ARTICLE_2, 
                        VALID_ARTICLE_3, 
                        VALID_ARTICLE_4
                        )
from authors.apps.authentication.tests.test_data import (
    VALID_USER_DATA,
    VALID_LOGIN_DATA
)
from authors.apps.articles.models import Articles, Tag
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

        self.assertEqual(
            response.data['article']['tagList'],
            ["cars", "bentlys"]
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
        update_url = reverse('crud-article', kwargs={
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
        update_url = reverse('crud-article', kwargs={
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
        update_url = reverse('crud-article', kwargs={
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
        get_article_url = reverse('crud-article', kwargs={
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
        get_article_url = reverse('crud-article', kwargs={
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
        get_article_url = reverse('crud-article', kwargs={
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
        get_article_url = reverse('crud-article', kwargs={
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
        get_article_url = reverse('crud-article', kwargs={
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

    def test_user_rating_your_own_article(self):
        token = self.create_user(VALID_USER_DATA)
        self.create_article(
            token=token,
            article=VALID_ARTICLE
        )
        article = Articles.objects.all().first()
        response = self.client.post(
            reverse('rate-article',
                    kwargs={'slug': article.slug}
                    ),
            data={"ratings": 3.0},
            HTTP_AUTHORIZATION=token
        )
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(response.data, response.json())

    def test_user_not_rating_your_own_articles(self):
        token = self.create_user(VALID_USER_DATA)
        self.create_article(
            token=token,
            article=VALID_ARTICLE
        )
        article = Articles.objects.all().first()
        token = self.create_user(VALID_USER_DATA_2)
        response = self.client.post(
            reverse('rate-article',
                    kwargs={'slug': article.slug}
                    ),
            data={"ratings": 3.0},
            HTTP_AUTHORIZATION=token
        )
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(response.data['message'],
                          "thanks for rating this article")

    def test_rating_out_of_range(self):
        token = self.create_user(VALID_USER_DATA)
        self.create_article(
            token=token,
            article=VALID_ARTICLE
        )
        article = Articles.objects.all().first()
        token = self.create_user(VALID_USER_DATA_2)
        response = self.client.post(
            reverse('rate-article',
                    kwargs={'slug': article.slug}
                    ),
            data={"ratings": 7.0},
            HTTP_AUTHORIZATION=token
        )
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(
            response.data['errors']['ratings'][0],
            'Ratings should be numbers between 0-5')


    def test_fetch_tags(self):
        '''Test fetching all tags available'''
        token = self.create_user(VALID_USER_DATA)

        response = self.client.post(
            self.create_articles,
            HTTP_AUTHORIZATION=token,
            data=VALID_ARTICLE_2,
            format='json'
        )

        get_tags = reverse('tags')

        response = self.client.get(
            get_tags,
            HTTP_AUTHORIZATION=token,
            format='json'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['results'],
            ["supreme", "mighty", "best"]
        )

    def test_fetch_tags_while_not_logged_in(self):
        '''Test fetching tags by a user that is not logged in'''
        get_tags = reverse('tags')

        response = self.client.get(
            get_tags
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_invalid_tag_format(self):
        '''Test for invalid tag format'''
        token = self.create_user(VALID_USER_DATA)

        response = self.client.post(
            self.create_articles,
            HTTP_AUTHORIZATION=token,
            data=INVALID_ARTICLE_2,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            response.data['errors'][0],
            "Tags must be in a list"
        )

    def test_already_existing_tag(self):
        '''Test for creating article with already existing tag'''
        token = self.create_user(VALID_USER_DATA)

        response = self.client.post(
            self.create_articles,
            HTTP_AUTHORIZATION=token,
            data=VALID_ARTICLE_2,
            format='json'
        )

        response = self.client.post(
            self.create_articles,
            HTTP_AUTHORIZATION=token,
            data=VALID_ARTICLE_3,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_model_str(self):
        '''test for the str method in the Tag models'''
        token = self.create_user(VALID_USER_DATA)

        response = self.client.post(
            self.create_articles,
            HTTP_AUTHORIZATION=token,
            data=VALID_ARTICLE_3,
            format='json'
        )
        tag_instance = Tag.objects.get(tag='supreme')
        self.assertEqual(str(tag_instance), tag_instance.tag)

    def test_filter_by_author(self):
        """
        test if we can search articles by author's name
        """
        token = self.create_user(VALID_USER_DATA)
        self.client.post(
                        self.create_articles, 
                        HTTP_AUTHORIZATION=token, 
                        data=VALID_ARTICLE_3, 
                        format='json'
                        )
        response = self.client.get(reverse('articles')
                                            + '?author=' + 'anyatijude', 
                                            format='json', 
                                            HTTP_AUTHORIZATION=token
                                            )
        self.assertEqual(response.status_code,
                        status.HTTP_200_OK
                        )

    def test_filter_by_title(self):
        """
        test if we can filter by title
        """
        token = self.create_user(VALID_USER_DATA)
        self.client.post(
                        self.create_articles, 
                        HTTP_AUTHORIZATION=token, 
                        data=VALID_ARTICLE_3, 
                        format='json'
                        )
        response = self.client.get(reverse('articles')
                                            + '?title=' + 'Prime Supreme Legends',
                                            format=json,
                                            HTTP_AUTHORIZATION=token
                                            )
        self.assertEqual(response.status_code,
                        status.HTTP_200_OK
                        )

    def test_get_article_with_reading_time(self):
        """ test if an article is returned with it's reading_time """
        token = self.create_user(VALID_USER_DATA)
        response = self.create_article(
            token=token,
            article=VALID_ARTICLE
        )
        get_article_url = reverse(
            'crud-article', kwargs={
            'slug': response.data['article']['slug']
        }
        )
        response = self.client.get(
            get_article_url
        )
        self.assertIn(
                    'less than a minute read', 
                    response.data['article']['reading_time']
                    )
        self.assertEqual(
                        response.status_code, 
                        status.HTTP_200_OK
                        )

    def test_get_article_with_longer_reading_time(self):
        """ 
        test if an article is returned with it's reading_time longer
        than a minute
        """
        token = self.create_user(VALID_USER_DATA)
        res = self.client.post(
                        self.create_articles, 
                        HTTP_AUTHORIZATION=token, 
                        data=VALID_ARTICLE_4, 
                        format='json'
                        )
        get_article_url = reverse('crud-article', kwargs={
            'slug': res.data['article']['slug']
        }
        )
        response = self.client.get(
            get_article_url
        )
        self.assertIn(
                    'minute read', 
                    response.data['article']['reading_time']
                    )
        self.assertEqual(
                        response.status_code, 
                        status.HTTP_200_OK
                        )


