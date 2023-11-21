from rest_framework import pagination
from rest_framework.response import Response

class CustomPagination(pagination.PageNumberPagination):
    def get_paginated_responsee(self, data):
        return Response({
            'data': data,  # Use 'data' instead of 'results'
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
        })
    page_size = 20
    page_size_query_param = 'page_size'
    # max_page_size = 50
    page_query_param = 'p'
    
    
    
class CustomPagination2(pagination.PageNumberPagination):
    page_size = 2000000
    page_size_query_param = 'page_size'
    # max_page_size = 50
    page_query_param = 'p'