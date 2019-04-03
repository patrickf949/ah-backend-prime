import jwt
from authors.settings import SECRET_KEY
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView, GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
from django.contrib.sites.shortcuts import get_current_site

from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer
)
from .validation import validate_registration


class RegistrationAPIView(GenericAPIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data.get('user', {})
        validate_registration(user)
        url=get_current_site(request)
        User.get_url(url)
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ActivateUserAPIView(GenericAPIView):
    def get(self, request, *args, **kwargs):
        token = kwargs.pop('token')
        user = jwt.decode(
            token,
            SECRET_KEY 
        )
        activateUser = User.objects.filter(pk=user['id']).first()

        if not activateUser.is_active:
            activateUser.is_active=True
            activateUser.save()
            return Response({
                'message':'your account has been activated successfully please login',
                'user':user    
            }, status=status.HTTP_202_ACCEPTED)
        

        return Response({
                'message':'your account is already active please login'  
            }, status=status.HTTP_202_ACCEPTED)


class LoginAPIView(GenericAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})

        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):

        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})

        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
