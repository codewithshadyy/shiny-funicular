from django.shortcuts import render

from rest_framework.generics import ListAPIView
from .serializers import MediaSerializer, PostSerializer
from .models import Post
from social.models import Follow
from rest_framework.pagination import CursorPagination

class FeedCursorPagination(CursorPagination):
    page_size = 20
    ordering = "-created_at"
    cursor_query_param = "cursor"

class FeedView(ListAPIView):
    serializer_class = PostSerializer
    pagination_class = FeedCursorPagination
    
    def get_queryset(self):
        following_ids = Follow.objects.filter(follower=self.request.user).values_list("following_id", flat=True)
        
        return (
            Post.objects.filter(author_id__in=following_ids)
            .select_related("author")
            .prefetch_related("media_items")
        )