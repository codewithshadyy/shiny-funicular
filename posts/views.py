from django.shortcuts import render

import uuid
from django.conf import settings
import boto3
from botocore.client import Config
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework.generics import ListAPIView
from .serializers import MediaSerializer, PostSerializer , MediaUploadRequestSerializer
from .models import Post, Media
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
        
def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        config=Config(signature_version="s3v4"),
    )        

class CreatePostWithMediaView(APIView):
    
    def post(self,request):
        content = request.data.get("content", "")
        media_type = request.data.get("media_type") 
        file_extension = request.data.get("file_extension", "")  
        
        post_type = "text"
        if media_type:
            post_type = media_type
        
        post = Post.objects.create(
            author=request.user,
            content=content,
            post_type=post_type,
        )
        
        if not media_type:
             return Response(PostSerializer(post).data, status=status.HTTP_201_CREATED)
         
        storage_key = f"posts/{post.id}/{uuid.uuid4()}.{file_extension}"   
        media = Media.objects.create(
            post=post,
            media_type=media_type,
            storage_key=storage_key,
            processing_status="pending",
        )
        
        s3_client = get_s3_client()
        presigned_url = s3_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                "Key": storage_key,
            },
            ExpiresIn=300, 
        )

        return Response(
            {
                "post": PostSerializer(post).data,
                "media_id": str(media.id),
                "upload_url": presigned_url,
                "storage_key": storage_key,
            },
            status=status.HTTP_201_CREATED,
        )   