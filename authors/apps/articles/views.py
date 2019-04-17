import json
from django.shortcuts import render
from rest_framework.response import Response
from .models import Articles, Tag, LikeDislike, Comment, FavoriteArticle
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly,
                                        AllowAny
                                        )
from rest_framework import generics, response, status
from authors.apps.profiles.models import Profile
from authors.apps.authentication.models import User
from . import serializers
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from django.shortcuts import get_object_or_404, get_list_or_404
from .pagination import ArticlePagination
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from authors.apps.articles.filters import ArticleFilter
from authors.settings import EMAIL_HOST_USER


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
        serializer = self.serializer_class(data=article, context={'request': request})
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
        """
        Add a rating for an article
        """
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


class CommentCreateList(generics.ListCreateAPIView):
    """
    Handle all crud operations for comments
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = serializers.CommentSerializer
    queryset = Comment.objects.all()

    def post(self, request, **kwargs):
        """
        Create a comment for a particular article
        """
        slug = kwargs.get('slug')
        comment = request.data
        parentId = kwargs.get('id')
        article = get_object_or_404(Articles, slug=slug)
        if parentId != 0:
            get_object_or_404(Comment, id=parentId, article=article)

        author = get_object_or_404(Profile, user_id=request.user.id)
        serialised_data = self.serializer_class(data=comment)

        serialised_data.is_valid(raise_exception=True)
        serialised_data.save(
            author=author,
            article=article,
            parentId=parentId
        )
        return Response(
            {"comment": serialised_data.data},
            status=status.HTTP_201_CREATED
        )

    def get(self, request, **kwargs):
        """
        Get comments for a particular article
        """
        slug = kwargs.pop('slug')
        comments = Comment.objects.filter(
            article_id=(get_object_or_404(
                Articles, slug=slug,
            )).pk
        )
        parent_id = kwargs.pop('id')
        if parent_id != 0:
            comments = get_list_or_404(comments, parentId=parent_id)
        serializer = self.serializer_class(comments, many=True)
        return Response({
            'message': serializer.data
        },
            status=status.HTTP_200_OK
        )


class CommentRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        comment = self.get_one_comment(kwargs.pop('id'))
        serialized_comment = self.serializer_class(comment)
        return Response(serialized_comment.data, status=status.HTTP_200_OK)

    def get_one_comment(self, commentId):
        comment = get_object_or_404(Comment, id=commentId)
        return comment

    def update(self, request, *args, **kwargs):
        comment = self.get_one_comment(kwargs.pop('id'))
        updated_comment = request.data
        if request.user.id != comment.author.user.id:
            return Response(
                {
                    "message": "You do not have permissions to edit this comment"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        if updated_comment['body'] == comment.body:
            return Response(
                {'message': 'No changes made to the comment'},
                status=status.HTTP_400_BAD_REQUEST
            )

        updated_comment['commentHistory'] = (
            comment.commentHistory+" \n[" + \
            str(comment.updatedAt) + "]'s version\n" + \
            comment.body
        )
        serializer = self.serializer_class(
            comment,
            updated_comment,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


    def delete(self, request, *args, **kwargs):
        comment = self.get_one_comment(kwargs.pop('id'))

        if request.user.id != comment.author.user.id:
            return Response(
                {
                    "message": "You do not have permissions to delete this comment"
                },
                status=status.HTTP_403_FORBIDDEN
            )
        comment.delete()
        return Response(
            {
                "message": "Comment has been successfully deleted"
            },
            status=status.HTTP_200_OK
        )

class ReportArticleView(generics.GenericAPIView):
    """
    class handling the view function for reporting articles
    """

    serializer_class = serializers.ArticleReportSerializer
    permission_classes = [IsAuthenticated, ]

    def post(self, request, slug):
        reporter = Profile.objects.get(user=request.user)
        article = Articles.objects.filter(slug=slug).first()
        
        data = {
            "violation": request.data['violation'] if 'violation' in request.data
            else ''
            }
        if reporter == article.author:
            return Response(
                            {
                            "message":
                            "You are not allowed to report your own article"
                            },
                            status=status.HTTP_403_FORBIDDEN
                            )
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(reporter=reporter, article=article)
        send_mail(
                subject = "Article reported as a violation",
                message = "Your article was reported as a violation. This is the reason: {}".format(data['violation']),
                from_email = EMAIL_HOST_USER,
                recipient_list = [article.author.user.email],
                fail_silently = False
                )
        return Response({
                "message" : 
                "Your report on this article has been recieved successfully", 
                "data": serializer.data  
        }, status=status.HTTP_201_CREATED)



class FavoriteArticleCreateList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = FavoriteArticle.objects.all()
    serializer_class = serializers.FavoriteArticleSerializer
    profile_serializer_class = serializers.ProfileSerializer
    article_serializer_class = serializers.ArticleSerializer


    def post(self, request, **kwargs):
        article = get_object_or_404(
            Articles, 
            slug=kwargs.get('slug')
        )
        favorited_by = get_object_or_404(
            Profile, 
            user_id=request.user.id
        )
        favorite = FavoriteArticle.objects.filter(
            favorited_by=favorited_by, 
            article=article
        )
        if not favorite:
            serializer = self.serializer_class(data={'is_favorite':True})
            serializer.is_valid(raise_exception=True)
            serializer.save(
                article=article,
                favorited_by=favorited_by
            )
            return Response(
                {"message": "You have favorited "+article.title},
                status=status.HTTP_200_OK
            )
        return Response(
            {"message": "You already favorited this article"},
            status=status.HTTP_200_OK
        )


    def get(self, request, **kwargs):
        """
        Get all users who have favorited a given article
        """
        article = Articles.objects.filter(slug=kwargs.pop('slug')).first()
        if not article:
            return Response({
                'message': 'This article does not exist'
            }, status=status.HTTP_404_NOT_FOUND)
        favorites = get_list_or_404(
            FavoriteArticle,
            article=article
        )
        serialized_favorites = self.serializer_class(favorites, many=True)

        favorited_by = [favorite.get('favorited_by') for favorite in serialized_favorites.data]

        return Response(
            {'favorited_by' : favorited_by},
            status=status.HTTP_200_OK
        )


class FavoriteArticleDestroy(generics.DestroyAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = FavoriteArticle.objects.all()
    serializer_class = serializers.FavoriteArticleSerializer
    lookup_field = 'slug'
    def delete(self, request, **kwargs):
        """
        Unfavorite an article
        """
        queryset = FavoriteArticle.objects.filter(favorited_by=Profile.objects.filter(user=request.user).first())
        queryset = queryset.filter(article_id=(Articles.objects.filter(slug=kwargs.get('slug')).first()).id).first()
        serializer = serializers.FavoriteArticleSerializer(queryset)

        if not queryset:
            return Response({
            'message': 'You have never favorited the article'
        },
            status=status.HTTP_400_BAD_REQUEST
        )
        queryset.delete()
        return Response({
            'message': 'You have unfavorited the article'
        },
            status=status.HTTP_200_OK
        )
