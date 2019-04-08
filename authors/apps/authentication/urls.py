from django.urls import path, include

from authors.apps.authentication.views import (
    LoginAPIView,
    RegistrationAPIView,
    UserRetrieveUpdateAPIView,
    PassordResetEmailView,
    ActivateUserAPIView
)

urlpatterns = [
    path('users/', UserRetrieveUpdateAPIView.as_view(), name='users'),
    path('users/register/', RegistrationAPIView.as_view(), name='register-user'),
    path('users/login/', LoginAPIView.as_view(), name='login-user'),
    path('users/register/<str:token>/activate/', ActivateUserAPIView.as_view(), name='activate-user'),
    path('users/password/reset/email/',
         PassordResetEmailView.as_view(), name='password-email'),
    path('users/password/<str:token>/reset/',
         PassordResetEmailView.as_view(), name='password-reset'),
]
