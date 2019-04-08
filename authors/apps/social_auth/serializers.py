from rest_framework import serializers
from authors.apps.social_auth import twitter_auth, google_auth, facebook_auth
from authors.apps.social_auth.register import register_user

class AuthSerializer(serializers.Serializer):
    '''Class to register a user if decoded token information is valid'''

    def validate_token(self, key, user_data):
        '''Function that registers a user if decoded token information is valid'''
        try:
            user_data[key]
        except:
            raise serializers.ValidationError(
                'This token is invalid'
            )
        if 'email' not in user_data:
            return "Email address not provided!"
        return register_user(email=user_data['email'], username=user_data['name'])


class TwitterAuthSerializer(AuthSerializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        '''Returns user information from decoded Twitter token'''
        user_info = twitter_auth.TwitterAuthHandler.validate_twitter_auth_tokens(auth_token)
        return self.validate_token('id_str', user_info)


class FacebookAuthSerializer(AuthSerializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        '''Returns user information from decoded Facebook token'''
        user_data = facebook_auth.FacebookAuthHandler.validate_facebook_auth_token(auth_token)
        return self.validate_token('id', user_data)


class GoogleAuthSerializer(AuthSerializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        '''Returns user information from decoded Google token'''
        user_data = google_auth.GoogleAuthHandler.validate_google_auth_token(auth_token)
        return self.validate_token('sub', user_data)
