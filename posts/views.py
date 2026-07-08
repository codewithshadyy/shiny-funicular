from django.core.cache import caches
redis_feed_cache = caches["default"]
from django.shortcuts import render
from django.core.files.storage import default_storage
from django.db.models import F
from django.db import IntegrityError


import uuid
from django.conf import settings
import boto3
from botocore.client import Config
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from rest_framework.generics import ListAPIView
from .serializers import MediaSerializer, PostSerializer , MediaUploadRequestSerializer, LikeSerailizer, CommentSerializer

from .models import Post, Media, Like, Comment, Notification
from social.models import Follow
from rest_framework.pagination import CursorPagination
from .tasks import process_media
from .tasks import fan_out_post_to_followers




ALLOWED_EXTENSIONS = {
    "image": {"jpg", "jpeg", "png", "webp"},
    "video": {"mp4", "mov", "webm"},
}

CONTENT_TYPES = {
    "jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp",
    "mp4": "video/mp4", "mov": "video/quicktime", "webm": "video/webm",
}

class FeedCursorPagination(CursorPagination):
    page_size = 20
    ordering = "-created_at"
    cursor_query_param = "cursor"

class FeedView(ListAPIView):
    serializer_class = PostSerializer
    pagination_class = FeedCursorPagination
    
    def get_queryset(self):
        following_ids = Follow.objects.filter(follower=self.request.user).values_list("following_id", flat=True)

        base_queryset = (
            Post.objects.filter(author_id__in=following_ids)
            .select_related("author")
            .prefetch_related("media_items")
        )
        cursor_param = self.request.query_params.get("cursor")

        if cursor_param:
            return base_queryset

        cache_key = f"feed:first_page:{self.request.user.id}"
        cached_ids = cache.get(cache_key)

        if cached_ids is not None:
            return (
                Post.objects.filter(id__in=cached_ids)
                .select_related("author")
                .prefetch_related("media_items")
                .order_by("-created_at")
            )

        page_size = self.pagination_class.page_size
        results = list(base_queryset[:page_size])
        cache.set(cache_key, [p.id for p in results], timeout=30)

        return base_queryset
        
        
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
            ext = file_extension.lower().lstrip(".")
            if media_type not in ALLOWED_EXTENSIONS:
                return Response({"error": "Invalid media_type"}, status=status.HTTP_400_BAD_REQUEST)
            if ext not in ALLOWED_EXTENSIONS[media_type]:
                return Response(
                    {"error": f"'{ext}' is not allowed for media_type '{media_type}'"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            file_extension = ext 
            
             
        # if media_type:
        #     post_type = media_type
        
        post = Post.objects.create(
            author=request.user,
            content=content,
            post_type=post_type,
        )
        
        fan_out_post_to_followers.delay(str(post.id))
        
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
        

class ConfirmMediaUploadView(APIView):
    def post(self, request, media_id):
        try:
            media = Media.objects.get(id=media_id, post__author=request.user)
        except Media.DoesNotExist:
            return Response({"error": "Media not found"}, status=status.HTTP_404_NOT_FOUND)

        
        if not default_storage.exists(media.storage_key):
            return Response(
                {"error": "File not found in storage - upload may have failed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        process_media.delay(str(media.id))

        return Response(
            {"media_id": str(media.id), "status": "processing_queued"},
            status=status.HTTP_202_ACCEPTED,
        )        
        
        
class PushFeedView(APIView):
    

    def get(self, request):
        raw_redis = redis_feed_cache.client.get_client()
        key = f"feed:push:{request.user.id}"

        
        post_ids = raw_redis.zrevrange(key, 0, 19)
        post_ids = [pid.decode() if isinstance(pid, bytes) else pid for pid in post_ids]

        posts = Post.objects.filter(id__in=post_ids).select_related("author").prefetch_related("media_items")
    
        posts_by_id = {str(p.id): p for p in posts}
        ordered_posts = [posts_by_id[pid] for pid in post_ids if pid in posts_by_id]

        serializer = PostSerializer(ordered_posts, many=True)
        return Response(serializer.data)        
    
    
    

class ToggleLikeView(APIView):
    
    serializer_class = LikeSerailizer
    
    def post(self,request, post_id):
        
        try:
            post = Post.objects.get(id=post_id)
        
        except Post.DoesNotExist:
            return Response({"error": "post not found"}, status=status.HTTP_404_NOT_FOUND)
        
        like, created = Like.objects.get_or_create(post=post, user=request.user)
        
        if created:
            Post.objects.filter(id=post_id).update(like_count=F("like_count") + 1)
            
            if post.author_id != request.user.id:
                Notification.objects.create(
                    recipient=post.author,
                    actor=request.user,
                    notification_type="like",
                    post=post,
                )
            
        post.refresh_from_db()
        
        return Response(
            {"liked": True, "like_count": post.like_count},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
        
    def delete(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        deleted_count, _ = Like.objects.filter(post=post, user=request.user).delete()
        if deleted_count > 0:
            
            Post.objects.filter(id=post_id).update(like_count=F("like_count") - 1)

        post.refresh_from_db()
        return Response({"liked": False, "like_count": post.like_count}, status=status.HTTP_200_OK)
            
        

class CommentCursorPagination(CursorPagination):
    page_size = 20
    ordering = "-created_at"
    
class CommentListCreateView(ListAPIView):
    
    serializer_class = CommentSerializer
    pagination_class = CommentCursorPagination

    def get_queryset(self):
        post_id = self.kwargs["post_id"]
        return Comment.objects.filter(post_id=post_id).select_related("author")

    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        content = request.data.get("content", "").strip()
        if not content:
            return Response({"error": "Comment content cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)
        if len(content) > 1000:
            return Response({"error": "Comment too long (max 1000 chars)"}, status=status.HTTP_400_BAD_REQUEST)

        comment = Comment.objects.create(post=post, author=request.user, content=content)
        Post.objects.filter(id=post_id).update(comment_count=F("comment_count") + 1)

        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)            