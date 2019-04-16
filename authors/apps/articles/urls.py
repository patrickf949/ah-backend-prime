from django.urls import path

from authors.apps.articles.views import (
    ArticleListCreate,
    ArticleRetrieveUpdateDestroy,
    RateArticleView,
    TagsView,
    VotesView,
    CommentCreateList,
    CommentRetrieveUpdateDestroy,
    ReportArticleView,
    FavoriteArticleCreateList,
    FavoriteArticleDestroy
)
from .models import LikeDislike
from .models import Articles

urlpatterns = [
    path(
        'articles/',
        ArticleListCreate.as_view(),
        name='articles'
    ),
    path(
        'articles/<str:slug>/',
        ArticleRetrieveUpdateDestroy.as_view(),
        name='crud-article'
    ),
    path(
        'articles/<str:slug>/rate/',
        RateArticleView.as_view(),
        name='rate-article'
    ),
    path(
        'tags/',
        TagsView.as_view(),
        name='tags'
    ),
    path(
        'articles/<str:slug>/like/',
        VotesView.as_view(
            vote_type=LikeDislike.LIKE,
            model=Articles
        ),
        name='article_like'
    ),
    path(
        'articles/<str:slug>/dislike/',
        VotesView.as_view(
            vote_type=LikeDislike.DISLIKE,
            model=Articles
        ),
        name='article_dislike'
    ),
    path(
        'articles/<str:slug>/comments/<int:id>/',
        CommentCreateList.as_view(),
        name='comments'
    ),
    path(
        'articles/comments/<int:id>/',
        CommentRetrieveUpdateDestroy.as_view(),
        name='crud-comment'
    ),
    path(
        'articles/<slug>/report/',
        ReportArticleView.as_view(),
        name='report_article'
    ),
    path(
        'articles/<str:slug>/favorite/',
        FavoriteArticleCreateList.as_view(),
        name='favorite-article'
    ),
    path(
        'articles/<str:slug>/unfavorite/',
        FavoriteArticleDestroy.as_view(),
        name='unfavorite-article'
    )

]
