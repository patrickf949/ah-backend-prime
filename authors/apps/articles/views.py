from django.shortcuts import render
from rest_framework import generics
from authors.apps.profiles.models import Profile
from . import serializers
from rest_framework.response import Response
from .models import Articles

from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from rest_framework import response, status


class ArticleListCreate(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    queryset = Articles.objects.all()
    serializer_class = serializers.ArticleSerializer

    def post(self,request):
        article = request.data
        serializer = self.serializer_class(data=article)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            author=Profile.objects.filter(
                user=request.user).first(),
                slug=Articles.get_slug(
                    article.get('title')
                )
        )
        return Response(
            {"article":serializer.data}, 
            status=status.HTTP_201_CREATED
        )
    
class ArticleRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Articles.objects.all()
    serializer_class = serializers.ArticleSerializer
    lookup_field = 'slug'

    def get(self, request, *args, **kwargs):
        request_response = self.get_one_article(kwargs.pop('slug'))
        request_data = request_response[0]
        request_status = request_response[1]

        return Response(request_data, status=request_status)

    def get_one_article(self, slug):
        article = Articles.objects.filter(slug=slug).first()

        if not article:
            return {'message':"The article does not exist"},status.HTTP_400_BAD_REQUEST
        serializer = self.serializer_class(
            article, partial=True
        )
        return {"article":serializer.data},status.HTTP_200_OK, article
        

    def update(self, request, *args, **kwargs):
        request_response = self.get_one_article(kwargs.pop('slug'))
        if request_response[1] != status.HTTP_200_OK:
            return Response(request_response[0], status=request_response[1])
        article = request_response[2]

        if request.user.id != article.author.user.id:
            return Response(
                {
                    "message":"You do not have permissions to edit this article"
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.serializer_class(
            article,
            data=request.data,
            partial=True,
            
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def delete(self, request, *args, **kwargs):
        request_response = self.get_one_article(kwargs.pop('slug'))
        if request_response[1] != status.HTTP_200_OK:
            return Response(request_response[0], status=request_response[1])

        article = request_response[2]

        if request.user.id != article.author.user.id:
            return Response(
                {
                    "message":"You do not have permissions to delete this article"
                },
                status=status.HTTP_403_FORBIDDEN
            )
        article.delete()
        return Response(
                {
                    "message":"Article has been successfully deleted"
                },
                status=status.HTTP_200_OK
            )
        
        