from django.conf import settings
from google.oauth2 import id_token
from google.auth.transport import requests

class GoogleAuthHandler:
    '''Class handles Google token validation and decoding'''

    @staticmethod
    def validate_google_auth_token(auth_token):
        '''This function decodes the token into data required from the user,
           all this with the help of the function verify_oauth2_token.
           The audience check ensures the token was issued to this
           application's OAuth client rather than to some other app.
        '''
        try:
            idinfo = id_token.verify_oauth2_token(
                auth_token,
                requests.Request(),
                audience=settings.GOOGLE_CLIENT_ID
            )
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            return idinfo
        except ValueError:
            return 'This token is invalid'
