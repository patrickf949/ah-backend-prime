from django.shortcuts import render
from rest_framework.response import Response
from .models import Articles, Tag, LikeDislike
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly, 
                                        AllowAny
                                        )
from rest_framework import generics, response, status
from authors.apps.profiles.models import Profile
from . import serializers
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from .pagination import ArticlePagination
from django.contrib.contenttypes.models import ContentType
from authors.apps.articles.filters import ArticleFilter

class ArticleListCreate(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    queryset = Articles.objects.all()
    serializer_class = serializers.ArticleSerializer
    pagination_class = ArticlePagination
    filter_class = ArticleFilter
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ('title', 'body', 'description', 'author__user__username')

    def post(self, request):
        article = request.data
        serializer = self.serializer_class(data=article, context={'request':request})
        serializer.is_valid(raise_exception=True)

        serializer.save(
            author=Profile.objects.filter(
                user=request.user).first(),
            slug=Articles.get_slug(
                article.get('title')
            )
        )
        return Response(
            {"article": serializer.data},
            status=status.HTTP_201_CREATED
        )

class ArticleRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Articles.objects.all()
    serializer_class = serializers.ArticleSerializer
    pagination_class = ArticlePagination
    lookup_field = 'slug'

    def get(self, request, *args, **kwargs):
        request_response = self.get_one_article(kwargs.pop('slug'))
        request_data = request_response[0]
        request_status = request_response[1]

        return Response(request_data, status=request_status)

    def get_one_article(self, slug):
        article = Articles.objects.filter(slug=slug).first()

        if not article:
            return {'message': "The article does not exist"}, status.HTTP_400_BAD_REQUEST
        serializer = self.serializer_class(
            article, partial=True
        )
        return {"article": serializer.data}, status.HTTP_200_OK, article

    def update(self, request, *args, **kwargs):
        request_response = self.get_one_article(kwargs.pop('slug'))
        if request_response[1] != status.HTTP_200_OK:
            return Response(request_response[0], status=request_response[1])
        article = request_response[2]

        if request.user.id != article.author.user.id:
            return Response(
                {
                    "message": "You do not have permissions to edit this article"
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
                    "message": "You do not have permissions to delete this article"
                },
                status=status.HTTP_403_FORBIDDEN
            )
        article.delete()
        return Response(
            {
                "message": "Article has been successfully deleted"
            },
            status=status.HTTP_200_OK
        )


class RateArticleView(generics.CreateAPIView):
    """
    view for rating articles
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = serializers.RateArticleSerializer

    def post(self, request, **kwargs):
        slug = kwargs.pop('slug')
        user = request.user
        article = Articles.objects.filter(slug=slug).first()
        data = {'user': article.author.id, 'article': article.pk,
                'ratings': request.data.get('ratings')}
        if user.id == article.author.id:
            return Response(
                {'error': 'you can not rate your own article'},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            serializers = self.serializer_class(data=data)
            serializers.is_valid(raise_exception=True)
            serializers.save()
            return Response(
                {'message': 'thanks for rating this article'},
                status=status.HTTP_201_CREATED
            )

class TagsView(generics.ListAPIView):
    '''This class returns all the tags available'''
    serializer_class = serializers.TagSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Tag.objects.all()


class VotesView(generics.CreateAPIView):
    '''View that handles the likes and dislikes routes'''
    serializer_class = serializers.ArticleSerializer
    model = None
    vote_type = None

    def post(self, request, slug):
        '''Post method handles liking and disliking an article'''
        obj = self.model.objects.get(slug=slug)
        try:
            likedislike = LikeDislike.objects.get(
                content_type=ContentType.objects.get_for_model(obj),
                object_id=obj.id, user=request.user
                )
            if likedislike.vote is not self.vote_type:
                likedislike.vote = self.vote_type
                likedislike.save(update_fields=['vote'])
            else:
                likedislike.delete()

        except LikeDislike.DoesNotExist:
            obj.votes.create(user=request.user, vote=self.vote_type)

        serializer = serializers.ArticleSerializer(obj)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
