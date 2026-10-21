from unittest.mock import patch, MagicMock

from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from authors.apps.articles.models import (
    Articles, Comment, FavoriteArticle, ArticleRating, Reaction, ReportArticle, Tag
)
from authors.apps.articles.serializers import (
    ArticleSerializer, CommentSerializer, TagsRelationSerializer
)
from authors.apps.articles.tests.base import ArticlesBaseTest
from authors.apps.articles.tests.test_data import VALID_ARTICLE
from authors.apps.authentication.models import User
from authors.apps.authentication.tests.test_data import VALID_USER_DATA


class ArticlesCoverageGapTest(ArticlesBaseTest):
    """Fills remaining coverage gaps for articles filters, models, views, and serializers."""

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            username='gapuser', email='gapuser@example.com', password='password123'
        )
        self.client.force_authenticate(user=self.user)

    def test_filter_by_tag(self):
        token = self.create_user(VALID_USER_DATA)
        self.create_article(VALID_ARTICLE, token)
        response = self.client.get(f"{self.create_articles}?tagsList=cars")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_article_models_str_and_methods(self):
        token = self.create_user(VALID_USER_DATA)
        create_res = self.create_article(VALID_ARTICLE, token)
        article = Articles.objects.get(slug=create_res.data['article']['slug'])

        # Articles __str__
        self.assertEqual(str(article), article.title)

        # Average rating when ratings exist
        ArticleRating.objects.create(article=article, user=self.user.profile, ratings=4)
        self.assertEqual(article.average_rating, 4.0)
        rating_obj = ArticleRating.objects.get(article=article)
        self.assertEqual(str(rating_obj), '4')

        # Reaction __str__ and emoji_for fallback
        self.assertEqual(Reaction.emoji_for('unknown_reaction'), '')
        ct = ContentType.objects.get_for_model(Articles)
        reaction = Reaction.objects.create(
            user=self.user, content_type=ct, object_id=article.id, reaction='heart'
        )
        self.assertIn('heart', str(reaction))

        # Comment __str__
        comment = Comment.objects.create(
            author=self.user.profile, article=article, body='test comment body', parentId=0
        )
        self.assertEqual(str(comment), 'test comment body')

        # ReportArticle __str__
        report = ReportArticle.objects.create(
            reporter=self.user.profile, article=article, violation='Spam violation'
        )
        self.assertEqual(str(report), 'Spam violation')

        # FavoriteArticle __str__
        fav = FavoriteArticle.objects.create(
            favorited_by=self.user.profile, article=article
        )
        self.assertEqual(str(fav), str(fav.pk))

    def test_serializers_uncovered_methods(self):
        tag_ser = TagsRelationSerializer()
        self.assertIsNotNone(tag_ser.get_queryset())

        mock_obj = MagicMock()
        mock_obj.comment.__all__ = ['comment1']
        self.assertEqual(ArticleSerializer().get_comments(mock_obj), ['comment1'])

        mock_obj.reply.__all__ = ['reply1']
        self.assertEqual(CommentSerializer().get_replies(mock_obj), ['reply1'])

    def test_comment_reaction_detail_get(self):
        token = self.create_user(VALID_USER_DATA)
        create_res = self.create_article(VALID_ARTICLE, token)
        article = Articles.objects.get(slug=create_res.data['article']['slug'])
        comment = Comment.objects.create(
            author=self.user.profile, article=article, body='comment for reactions', parentId=0
        )
        url = reverse('comment-reactions', kwargs={'id': comment.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_discovery_feed_invalid_limit_query_param(self):
        url = reverse('latest-articles') + "?limit=invalid_not_an_int"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_comment_replies(self):
        token = self.create_user(VALID_USER_DATA)
        create_res = self.create_article(VALID_ARTICLE, token)
        slug = create_res.data['article']['slug']
        article = Articles.objects.get(slug=slug)
        parent_comment = Comment.objects.create(
            author=self.user.profile, article=article, body='parent comment', parentId=0
        )
        Comment.objects.create(
            author=self.user.profile, article=article, body='child reply', parentId=parent_comment.id
        )
        url = reverse('comments', kwargs={'slug': slug, 'id': parent_comment.id})
        response = self.client.get(url, HTTP_AUTHORIZATION=token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reacted_articles_view_get(self):
        token = self.create_user(VALID_USER_DATA)
        create_res = self.create_article(VALID_ARTICLE, token)
        slug = create_res.data['article']['slug']
        article = Articles.objects.get(slug=slug)
        ct = ContentType.objects.get_for_model(Articles)
        Reaction.objects.create(
            user=self.user, content_type=ct, object_id=article.id, reaction='heart'
        )

        url = reverse('reacted-articles')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_upload_image_size_not_an_integer(self):
        url = reverse('upload-image-url')
        data = {'filename': 'img.jpg', 'contentType': 'image/jpeg', 'size': 'not-an-int'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'size must be an integer.')

    @patch('authors.apps.articles.views.boto3.client')
    def test_upload_image_s3_exception(self, mock_boto):
        mock_boto.return_value.generate_presigned_url.side_effect = Exception('s3 connection failure')
        url = reverse('upload-image-url')
        data = {'filename': 'img.jpg', 'contentType': 'image/jpeg', 'size': 1024}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
