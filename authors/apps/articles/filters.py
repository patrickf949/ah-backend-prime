from django_filters import rest_framework as filters
from django_filters import FilterSet
from authors.apps.articles.models import Articles

class ArticleFilter(FilterSet):
    """
    class handling the filtering of articles:
        filter-params:
        - title
        - author
        - keywords
        - tagList
    returns article depending on the supplied param
    """
    author = filters.CharFilter('author__user__username',
                                lookup_expr='icontains'
                                )
    title = filters.CharFilter(lookup_expr='icontains')
    tagsList = filters.CharFilter('tagsList', method='filter_tags')

    class Meta:
        model = Articles
        fields = ('author', 'title', 'tagsList')

    def filter_tags(self, queryset, tag, value):
        return queryset.filter(tagsList__tag__icontains=value)
