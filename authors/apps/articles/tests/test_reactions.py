from rest_framework import status

from .base import ArticlesBaseTest
from .test_data import VALID_ARTICLE, VALID_ARTICLE_2
from authors.apps.authentication.tests.test_data import (
    VALID_USER_DATA,
    VALID_USER_DATA_2,
)


class TestEmojiReactions(ArticlesBaseTest):
    '''Tests for the multi-emoji reactions API'''

    def react(self, token, slug, reaction):
        return self.client.post(
            f'/api/v1/articles/{slug}/react/',
            HTTP_AUTHORIZATION=token,
            data={'reaction': reaction},
            format='json'
        )

    def create_article_slug(self, token, article=VALID_ARTICLE):
        response = self.create_article(article, token)
        return response.data['article']['slug']

    def test_react_with_emoji(self):
        '''A user can react to an article with any supported emoji'''
        token = self.create_user(VALID_USER_DATA)
        slug = self.create_article_slug(token)
        response = self.react(token, slug, 'fire')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        breakdown = {
            item['reaction']: item['count']
            for item in response.data['reactions']['breakdown']
        }
        self.assertEqual(breakdown['fire'], 1)
        self.assertEqual(response.data['reactions']['total'], 1)

    def test_react_toggle_off(self):
        '''Reacting twice with the same emoji removes the reaction'''
        token = self.create_user(VALID_USER_DATA)
        slug = self.create_article_slug(token)
        self.react(token, slug, 'love')
        response = self.react(token, slug, 'love')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['reactions']['total'], 0)

    def test_multiple_emojis_by_same_user(self):
        '''A user can hold several different emoji reactions at once'''
        token = self.create_user(VALID_USER_DATA)
        slug = self.create_article_slug(token)
        self.react(token, slug, 'clap')
        response = self.react(token, slug, 'insightful')
        self.assertEqual(response.data['reactions']['total'], 2)

    def test_like_and_dislike_are_mutually_exclusive(self):
        '''Reacting like then dislike replaces the like'''
        token = self.create_user(VALID_USER_DATA)
        slug = self.create_article_slug(token)
        self.react(token, slug, 'like')
        response = self.react(token, slug, 'dislike')
        self.assertEqual(response.data['likes'], 0)
        self.assertEqual(response.data['dislikes'], 1)

    def test_invalid_reaction_rejected(self):
        '''An unsupported reaction name returns a validation error'''
        token = self.create_user(VALID_USER_DATA)
        slug = self.create_article_slug(token)
        response = self.react(token, slug, 'banana')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reaction_requires_authentication(self):
        '''Anonymous users cannot react'''
        token = self.create_user(VALID_USER_DATA)
        slug = self.create_article_slug(token)
        response = self.client.post(
            f'/api/v1/articles/{slug}/react/',
            data={'reaction': 'like'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reaction_breakdown_endpoint(self):
        '''GET reactions returns per-emoji counts and viewer state'''
        token = self.create_user(VALID_USER_DATA)
        slug = self.create_article_slug(token)
        self.react(token, slug, 'wow')
        response = self.client.get(
            f'/api/v1/articles/{slug}/reactions/',
            HTTP_AUTHORIZATION=token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 1)
        self.assertIn('wow', response.data['viewer_reactions'])
        wow = next(item for item in response.data['breakdown']
                   if item['reaction'] == 'wow')
        self.assertEqual(wow['emoji'], '😮')
        self.assertTrue(wow['viewer_reacted'])

    def test_comment_reactions(self):
        '''A user can react to a comment with an emoji'''
        token = self.create_user(VALID_USER_DATA)
        slug = self.create_article_slug(token)
        comment = self.create_comment(token, slug, 0)
        comment_id = comment.data['comment']['id']
        response = self.client.post(
            f'/api/v1/articles/comments/{comment_id}/react/',
            HTTP_AUTHORIZATION=token,
            data={'reaction': 'laugh'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['reactions']['total'], 1)

    def test_reactions_from_multiple_users(self):
        '''Reaction counts aggregate across users'''
        token_one = self.create_user(VALID_USER_DATA)
        slug = self.create_article_slug(token_one)
        self.react(token_one, slug, 'fire')
        token_two = self.create_user(VALID_USER_DATA_2)
        response = self.react(token_two, slug, 'fire')
        breakdown = {
            item['reaction']: item['count']
            for item in response.data['reactions']['breakdown']
        }
        self.assertEqual(breakdown['fire'], 2)
