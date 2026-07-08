from rest_framework import serializers
from .models import Post, Media, Like, Comment, Notification

class MediaSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Media
        fields = [
            "id", "media_type", "storage_key", "processing_status",
            "duration_seconds", "thumbnail_key", "width", "height", "order",
        ]

class PostSerializer(serializers.ModelSerializer):
    author_handle = serializers.CharField(source="author.handle", read_only=True)
    media_items = MediaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Post
        fields =  [
            "id", "author_handle", "post_type", "content",
            "like_count", "comment_count", "created_at", "media_items",
        ]
        read_only_fields = ["like_count", "comment_count", "created_at"]
        
class MediaUploadRequestSerializer(serializers.Serializer):
    media_type = serializers.ChoiceField(choices=["image", "video"])
    file_extension = serializers.CharField(max_length=10)        
    
class CommentSerializer(serializers.ModelSerializer):
    author_handle = serializers.CharField(source="author.handle", read_only=True)
    
    class Meta:
        model =Comment
        fields = ["id","post", "author_handle", "content", "created_at"]   
        read_only_fields =["id", "author_handle", "created_at"] 

class LikeSerailizer(serializers.ModelSerializer):
    
    class Meta:
        model = Like
        fields = ["id", "post", "user","created_at"]        
        
        
class NotificationSerializer(serializers.ModelSerializer):
    actor_handle = serializers.CharField(source="actor.handle", read_only=True)
    post_id = serializers.UUIDField(source="post.id", read_only=True, allow_null=True)

    class Meta:
        model = Notification
        fields = [
            "id", "notification_type", "actor_handle", "post_id",
            "is_read", "created_at",
        ]        