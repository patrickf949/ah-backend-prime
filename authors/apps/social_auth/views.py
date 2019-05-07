from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, GenericAPIView
from rest_framework.permissions import AllowAny
from authors.apps.authentication.renderers import UserJSONRenderer
from authors.apps.social_auth.serializers import FacebookAuthSerializer, GoogleAuthSerializer, TwitterAuthSerializer


class TwitterAuthView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = TwitterAuthSerializer

    def post(self, request):
        user = request.data.get('user_token', {})
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        return Response(data, status=status.HTTP_200_OK)


class FacebookAuthView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = FacebookAuthSerializer

    def post(self, request):
        user = request.data.get('user_token', {})
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        return Response(data, status=status.HTTP_200_OK)


class GoogleAuthView(GenericAPIView):
    """
    class that handles authentication through Google+
    """
    permission_classes = (AllowAny,)
    serializer_class = GoogleAuthSerializer

    def post(self, request):
        """
        Post method that handles registration of user on system
        """
        user = request.data.get('user_token', {})
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        return Response(data, status=status.HTTP_200_OK)
