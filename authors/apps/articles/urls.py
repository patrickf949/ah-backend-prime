from django.urls import path

from authors.apps.articles.views import (
    ArticleListCreate,
    ArticleRetrieveUpdateDestroy,
    RateArticleView,
    TagsView,
    VotesView
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
    )
]
