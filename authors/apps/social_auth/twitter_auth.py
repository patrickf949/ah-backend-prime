import twitter
from authors.settings import TWITTER_CONSUMER_API_KEY, TWITTER_CONSUMER_API_SECRET

class TwitterAuthHandler:
    '''This Class handles twitter token decoding and verification'''

    @staticmethod
    def validate_twitter_auth_tokens(tokens):
        '''This function splits the validation tokens into the api_key and api_secret, 
           decodes all the tokens(with consumer api and consumer secret) into the data 
           required from the user and then returns the data in dictionary format
        '''
        if len(tokens.split(" ")) != 2:
            return "Invalid. Please provide two tokens!"

        access_token_key = tokens.split(" ")[0]
        access_token_secret = tokens.split(" ")[1]
        try:
            consumer_api_key = TWITTER_CONSUMER_API_KEY
            consumer_api_secret = TWITTER_CONSUMER_API_SECRET
            api = twitter.Api(
                consumer_key=consumer_api_key,
                consumer_secret=consumer_api_secret,
                access_token_key=access_token_key,
                access_token_secret=access_token_secret
            )
            user_profile_info = api.VerifyCredentials(include_email=True)
            return user_profile_info.__dict__
        except twitter.error.TwitterError:
            return 'Please provide valid access tokens'
