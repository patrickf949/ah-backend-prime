from django.shortcuts import get_object_or_404
from rest_framework.generics import (
                                    UpdateAPIView, 
                                    RetrieveAPIView,
                                    GenericAPIView
                                    )
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        AllowAny, 
                                        IsAuthenticated
                                        )
from .permissions import IsOwnerOrReadOnly
from .models import Profile
from .renderers import ProfileJSONRenderer
from .serializers import (ProfileSerializer,
                            )
from authors.apps.authentication.models import User
from authors.apps.authentication.renderers import UserJSONRenderer
from authors.apps.authentication.serializers import UserSerializer


class ListProfileView(GenericAPIView):
    """
    class that implements fetching all users' profiles
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer
    renderer_classes = (ProfileJSONRenderer,)

    def get(self, request, *args, **kwargs):
        queryset = Profile.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateProfileView(GenericAPIView):
    """
    allows the current user to update their profile
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsOwnerOrReadOnly,]
    renderer_classes = (ProfileJSONRenderer,)
    lookup_field = "username"

    def get_object(self):
        return get_object_or_404(self.get_queryset(), 
                                user__username=self.kwargs.get("username")
                                )

    def put(self, request, *args, **kwargs):
        profile = self.get_object()
        user_name = self.kwargs.get('username')
        logged_in_user = request.user.username   
        if str(user_name) == str(logged_in_user):
            serializer = self.serializer_class(profile,
                                                data=request.data
                                                )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "Profile Updated successfully"})
        else:
            return Response({"message": "You do not have privileges to edit this profile"},
                            status=status.HTTP_403_FORBIDDEN
                            )
    
class ProfileRetrieveAPIView(GenericAPIView):
    """
    class handling returning the profile of a single user
    """
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, username, *args, **kwargs):
        profile = Profile.objects.select_related('user').get(
                user__username=username)
        serializer = self.serializer_class(profile)
        profile = {'profile': serializer.data}
        return Response(profile, status=status.HTTP_200_OK)

class UserListAPIView(GenericAPIView):
    """
    returns list of all users and their profiles
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    renderer_classes = (UserJSONRenderer,)

    def get(self, request, *args, **kwargs):
        queryset = User.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

