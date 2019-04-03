from django.urls import path

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView, ActivateUserAPIView
)

urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view(), name='update-user'),
    path('users/register/', RegistrationAPIView.as_view(), name='register-user'),
    path('users/login/', LoginAPIView.as_view(), name='login-user'),
    path('users/register/<str:token>/activate/', ActivateUserAPIView.as_view(), name='activate-user')
]
