from rest_framework.pagination import PageNumberPagination

class ArticlePagination(PageNumberPagination):
    """
    class that handles custom pagination of articles
    """
    page_query_param = 'page_size'
    page_size = 5
    last_page_strings = ('END', )
    max_page_size = 100
