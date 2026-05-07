from rest_framework.pagination import CursorPagination, LimitOffsetPagination
from rest_framework.response import Response


class CustomLimitOffsetPagination(LimitOffsetPagination):
    limit_query_param = "limit"
    offset_query_param = "offset"

    def paginate_queryset(self, queryset, request, view=None):
        self.limit = self.get_limit(request)
        if not self.limit:
            return None
        
        self.count = self.get_count(queryset)
        self.offset = self.get_offset(request)
        self.request = request

        if self.offset >= self.count or self.count == 0:
            return []
        
        return list(queryset[self.offset:self.offset + self.limit])

    def get_offset(self, request):
        try:
            value = request.query_params.get(self.offset_query_param, "0")
            return max(0, int(value))
        except (TypeError, ValueError):
            return 0

    def get_limit(self, request):
        if not self.limit_query_param:
            return self.default_limit
        
        try:
            value = request.query_params.get(self.limit_query_param, str(self.default_limit))
            limit = int(value)
            return max(1, min(limit, self.max_limit)) if hasattr(self, 'max_limit') else max(1, limit)
        except (TypeError, ValueError):
            return self.default_limit

    def get_paginated_response(self, data):
        total = self.count
        limit = self.limit
        
        if total == 0:
            pages_count = 0
            current_page = 0
        else:
            pages_count = (total + limit - 1) // limit
            current_page = (self.offset // limit) + 1

        return Response({
            "pages_count": pages_count,
            "items_per_page": limit,
            "current_page_items_count": len(data),
            "current_page": current_page,
            "total_items": total,
            "items": data,
        })


class StandardCursorPagination(CursorPagination):
    page_size = 50
    page_size_query_param = "limit"
    cursor_query_param = "cursor"
    max_page_size = 100
