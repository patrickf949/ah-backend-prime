import jwt
from django.conf import settings
from rest_framework import authentication, exceptions
from .models import User


class JWTAuthentication(authentication.BaseAuthentication):

    """
    class handling authentication of JSON web tokens provided by the user
    """
    authentication_header_prefix = 'Bearer'

    def authenticate(self, request):
        """
        method that checks the authorization header of any request regardless
        of whether authentication is required or not required

        """
        request.user = None

        auth_header = authentication.get_authorization_header(request).split()
        prefix = self.authentication_header_prefix.lower()

        if not auth_header:
            return None

        if len(auth_header) == 1:
            return None

        elif len(auth_header) > 2:
            msg = 'Your token is invalid'
            raise exceptions.AuthenticationFailed(msg)

        print(auth_header)
        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if prefix.lower() != 'Bearer'.lower():
            msg = 'Bearer prefix missing in authorization headers'
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(request, token)

    def authenticate_credentials(self, request, token):
        """
        method authenticates the given credentials
        if authentication is successful, returns user, token
        if authentication is not successful, throw an error
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
        except BaseException:
            raise exceptions.AuthenticationFailed(
                'Invalid authentication. Token could not be decoded')

        try:
            user = User.objects.get(pk=payload['id'])
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed(
                'No user matching this token exists')

        if not user.is_active:
            raise exceptions.AuthenticationFailed(
                'This user is nolonger active or is deactivated')
        return (user, token)
