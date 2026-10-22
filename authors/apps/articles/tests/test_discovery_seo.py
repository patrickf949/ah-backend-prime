from rest_framework import status

from .base import ArticlesBaseTest
from .test_data import VALID_ARTICLE, VALID_ARTICLE_2, VALID_ARTICLE_3
from authors.apps.authentication.tests.test_data import (
    VALID_USER_DATA,
    VALID_USER_DATA_2,
)


class TestArticleDiscovery(ArticlesBaseTest):
    '''Tests for latest, trending and popular article endpoints'''

    def setUp(self):
        super().setUp()
        self.token = self.create_user(VALID_USER_DATA)
        self.slug_one = self.create_article(
            VALID_ARTICLE, self.token).data['article']['slug']
        self.slug_two = self.create_article(
            VALID_ARTICLE_2, self.token).data['article']['slug']
        self.slug_three = self.create_article(
            VALID_ARTICLE_3, self.token).data['article']['slug']

    def test_latest_articles(self):
        '''Latest endpoint returns newest articles first'''
        response = self.client.get('/api/v1/articles/latest/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        slugs = [article['slug'] for article in response.data['articles']]
        self.assertEqual(slugs[0], self.slug_three)

    def test_latest_articles_respects_limit(self):
        '''The limit query parameter caps the number of results'''
        response = self.client.get('/api/v1/articles/latest/?limit=2')
        self.assertEqual(len(response.data['articles']), 2)

    def test_trending_articles(self):
        '''Trending ranks the article with most comments/reactions first'''
        self.create_comment(self.token, self.slug_one, 0)
        self.create_comment(self.token, self.slug_one, 0)
        self.client.post(
            f'/api/v1/articles/{self.slug_one}/react/',
            HTTP_AUTHORIZATION=self.token,
            data={'reaction': 'fire'},
            format='json'
        )
        response = self.client.get('/api/v1/articles/trending/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        slugs = [article['slug'] for article in response.data['articles']]
        self.assertEqual(slugs[0], self.slug_one)

    def test_popular_articles(self):
        '''Popular ranks by positive reactions and favorites'''
        token_two = self.create_user(VALID_USER_DATA_2)
        for reaction in ('love', 'clap'):
            self.client.post(
                f'/api/v1/articles/{self.slug_two}/react/',
                HTTP_AUTHORIZATION=token_two,
                data={'reaction': reaction},
                format='json'
            )
        self.client.post(
            f'/api/v1/articles/{self.slug_two}/favorite/',
            HTTP_AUTHORIZATION=token_two
        )
        # dislikes should not boost popularity
        self.client.post(
            f'/api/v1/articles/{self.slug_one}/react/',
            HTTP_AUTHORIZATION=token_two,
            data={'reaction': 'dislike'},
            format='json'
        )
        response = self.client.get('/api/v1/articles/popular/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        slugs = [article['slug'] for article in response.data['articles']]
        self.assertEqual(slugs[0], self.slug_two)


class TestArticleSeo(ArticlesBaseTest):
    '''Tests for SEO metadata endpoints'''

    def setUp(self):
        super().setUp()
        self.token = self.create_user(VALID_USER_DATA)
        self.slug = self.create_article(
            VALID_ARTICLE, self.token).data['article']['slug']

    def test_article_seo_endpoint(self):
        '''SEO endpoint returns meta tags and JSON-LD structured data'''
        response = self.client.get(f'/api/v1/articles/{self.slug}/seo/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        meta = response.data['meta']
        self.assertEqual(meta['meta_title'], VALID_ARTICLE['title'])
        self.assertIn(self.slug, meta['canonical_url'])
        self.assertIn('cars', meta['keywords'])
        structured = response.data['structured_data']
        self.assertEqual(structured['@type'], 'Article')
        self.assertEqual(structured['headline'], VALID_ARTICLE['title'])

    def test_article_serializer_includes_seo(self):
        '''Article payloads embed SEO metadata'''
        response = self.client.get(f'/api/v1/articles/{self.slug}/')
        seo = response.data['article']['seo']
        self.assertIn('meta_description', seo)
        self.assertIn('canonical_url', seo)

    def test_sitemap(self):
        '''Sitemap lists article canonical URLs'''
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.slug, response.content.decode())

    def test_robots(self):
        '''robots.txt points crawlers at the sitemap'''
        response = self.client.get('/robots.txt')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Sitemap:', response.content.decode())

    def test_rss_feed(self):
        '''RSS feed contains the latest articles'''
        response = self.client.get('/feed/rss/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(VALID_ARTICLE['title'], response.content.decode())
