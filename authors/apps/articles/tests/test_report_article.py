import json
from rest_framework import status, response
from django.urls import reverse
from .base import ArticlesBaseTest
from .test_data import VALID_ARTICLE
from authors.apps.authentication.tests.test_data import (
    VALID_USER_DATA, VALID_USER_DATA_2
)
from rest_framework.test import APIClient, APITestCase
from .base import BaseTest

class TestReportArticle(ArticlesBaseTest):
    """
    class testing reporting of an article
    """

    def test_report_article_success(self):
        """
        tests if an article can be reported successfully
        """
        token = self.create_user(VALID_USER_DATA)
        report_data = self.client.post(
            self.create_articles,
            HTTP_AUTHORIZATION=token,
            data=VALID_ARTICLE,
            format='json'
        )
        reason = {"violation": "This is not TIA"}
        token_2 = self.create_user(VALID_USER_DATA_2)
        response = self.client.post(
                                    '/api/v1/articles/{}/report/'.format
                                    (report_data.data['article']['slug']),
                                    HTTP_AUTHORIZATION=token_2,
                                    data=reason, format="json"
                                    )
        self.assertEqual(
                        response.status_code, 
                        status.HTTP_201_CREATED
                        )
        self.assertIn(
                    response.data['message'], 
                    "Your report on this article has been recieved successfully" 
        )

    def test_report_article_forbidden(self):
        """
        tests if a user is forbidden from reporting his own article
        """
        token = self.create_user(VALID_USER_DATA)
        report_data = self.client.post(
            self.create_articles,
            HTTP_AUTHORIZATION=token,
            data=VALID_ARTICLE,
            format='json'
        )
        reason = {"violation": "This article is offensive"}
        response = self.client.post(
                                    '/api/v1/articles/{}/report/'.format
                                    (report_data.data['article']['slug']),
                                    HTTP_AUTHORIZATION=token,
                                    data=reason, format="json"
                                    )
        self.assertEqual(
                        response.status_code, 
                        status.HTTP_403_FORBIDDEN
                        )
        self.assertEqual(
                    response.data['message'], 
                    "You are not allowed to report your own article" 
        )

