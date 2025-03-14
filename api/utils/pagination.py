from rest_framework.pagination import PageNumberPagination


class ContentPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = 'page'


class CommentPagination(PageNumberPagination):
    page_size = 35
    page_size_query_param = 'page_size'
    page_query_param = 'page'
