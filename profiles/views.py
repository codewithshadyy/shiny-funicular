from django.shortcuts import render

import uuid
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import CursorPagination
from accounts.models import Creator
from .models import Profile
from .serializers import ProfileSerializer, UserSearchSerializer
from posts.models import Post
from posts.serializers import PostSerializer


class ProfileDetailView(APIView):
  

    def get(self, request, handle):
        profile = get_object_or_404(Profile, user__handle=handle)
        return Response(ProfileSerializer(profile, context={"request": request}).data)

    def patch(self, request, handle):
        if request.user.handle != handle:
            return Response({"error": "You can only edit your own profile"}, status=status.HTTP_403_FORBIDDEN)

        profile = get_object_or_404(Profile, user__handle=handle)
        for field in ["bio", "location", "website"]:
            if field in request.data:
                setattr(profile, field, request.data[field])
        profile.save()
        return Response(ProfileSerializer(profile, context={"request": request}).data)


class UserPostsCursorPagination(CursorPagination):
    page_size = 20
    ordering = "-created_at"


class UserPostsView(ListAPIView):
    
    serializer_class = PostSerializer
    pagination_class = UserPostsCursorPagination

    def get_queryset(self):
        handle = self.kwargs["handle"]
        return (
            Post.objects.filter(author__handle=handle)
            .select_related("author")
            .prefetch_related("media_items")
        )


class UserSearchView(ListAPIView):
   
    serializer_class = UserSearchSerializer

    def get_queryset(self):
        query = self.request.query_params.get("q", "").strip()
        if not query:
            return Creator.objects.none()
        return Creator.objects.filter(
            Q(handle__istartswith=query) | Q(username__istartswith=query)
        ).select_related("profile")[:20]
