from django.urls import path
from authors.apps.social_auth.views import (
    FacebookAuthView, GoogleAuthView, TwitterAuthView
)

urlpatterns = [
    path('auth/facebook/', FacebookAuthView.as_view()),
    path('auth/google/', GoogleAuthView.as_view()),
    path('auth/twitter/', TwitterAuthView.as_view()),
]
