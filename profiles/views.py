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
from django.core.files.storage import default_storage
from media_storage.utils import get_s3_client
from django.conf import settings


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



class AvatarUploadRequestView(APIView):
    def post(self, request):
        file_extension = request.data.get("file_extension", "").lower().lstrip(".")
        allowed = {"jpg", "jpeg", "png", "webp"}
        if file_extension not in allowed:
            return Response({"error": f"Extension must be one of {allowed}"}, status=status.HTTP_400_BAD_REQUEST)

        storage_key = f"avatars/{request.user.id}/{uuid.uuid4()}.{file_extension}"

        s3_client = get_s3_client()
        upload_url = s3_client.generate_presigned_url(
            "put_object",
            Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": storage_key},
            ExpiresIn=300,
        )

        return Response({"upload_url": upload_url, "storage_key": storage_key})


class AvatarConfirmView(APIView):
    def post(self, request):
        storage_key = request.data.get("storage_key")
        if not storage_key or not storage_key.startswith(f"avatars/{request.user.id}/"):
            
            return Response({"error": "Invalid storage key"}, status=status.HTTP_400_BAD_REQUEST)

        if not default_storage.exists(storage_key):
            return Response({"error": "File not found - upload may have failed"}, status=status.HTTP_400_BAD_REQUEST)

        Profile.objects.filter(user=request.user).update(avatar_key=storage_key)
        return Response({"message": "Avatar updated"})