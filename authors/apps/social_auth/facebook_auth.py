import facebook

class FacebookAuthHandler:
    '''This class handles facebook token decoding'''

    @staticmethod
    def validate_facebook_auth_token(auth_token):
        """
        This function decodes the received token into data required from the user, 
        all this with the help of facebook's GraphAPI. Data received includes email,
        name and profile picture
        """
        try:
            graph = facebook.GraphAPI(access_token=auth_token)
            profile = graph.request('/me?fields=name,email,picture')
            return profile
        except Exception:
            return 'This token is invalid'
