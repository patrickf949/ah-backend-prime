from django.urls import path
from .views import (ListProfileView, 
                    UpdateProfileView, 
                    ProfileRetrieveAPIView, 
                    UserListAPIView
                    )


urlpatterns = [
    path('profiles/', ListProfileView.as_view(), name='user-profiles'),
    path('profiles/<username>', ProfileRetrieveAPIView.as_view(), name='get-profile'),
    path('profiles/<username>/edit', UpdateProfileView.as_view(), name='update-profile'),
    path('userslist/', UserListAPIView.as_view(), name='users-list')
]