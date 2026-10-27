from rest_framework import serializers
from authors.apps.social_auth import twitter_auth, google_auth, facebook_auth
from authors.apps.social_auth.models import SocialAccount
from authors.apps.social_auth.register import register_social_user

class AuthSerializer(serializers.Serializer):
    '''Base class: turns decoded provider data into a logged-in user'''

    provider = None

    def validate_token(self, key, user_data):
        '''Registers or logs in a user if decoded token information is valid'''
        try:
            provider_user_id = user_data[key]
        except (TypeError, KeyError):
            raise serializers.ValidationError(
                'This token is invalid'
            )
        if not user_data.get('email'):
            return "Email address not provided!"

        full_name = user_data.get('name') or ''
        image = (
            user_data.get('picture')
            or user_data.get('profile_image_url_https')
            or user_data.get('profile_image_url')
            or ''
        )
        if isinstance(image, dict):
            image = image.get('data', {}).get('url', '')

        return register_social_user(
            provider=self.provider,
            provider_user_id=provider_user_id,
            email=user_data['email'],
            username=user_data.get('name') or user_data.get('screen_name'),
            full_name=full_name,
            image=image
        )


class TwitterAuthSerializer(AuthSerializer):
    auth_token = serializers.CharField()
    provider = SocialAccount.TWITTER

    def validate_auth_token(self, auth_token):
        '''Returns user information from decoded Twitter token'''
        user_info = twitter_auth.TwitterAuthHandler.validate_twitter_auth_tokens(auth_token)
        return self.validate_token('id_str', user_info)


class FacebookAuthSerializer(AuthSerializer):
    auth_token = serializers.CharField()
    provider = SocialAccount.FACEBOOK

    def validate_auth_token(self, auth_token):
        '''Returns user information from decoded Facebook token'''
        user_data = facebook_auth.FacebookAuthHandler.validate_facebook_auth_token(auth_token)
        return self.validate_token('id', user_data)


class GoogleAuthSerializer(AuthSerializer):
    auth_token = serializers.CharField()
    provider = SocialAccount.GOOGLE

    def validate_auth_token(self, auth_token):
        '''Returns user information from decoded Google token'''
        user_data = google_auth.GoogleAuthHandler.validate_google_auth_token(auth_token)
        return self.validate_token('sub', user_data)
