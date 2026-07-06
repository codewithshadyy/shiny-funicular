from rest_framework import serializers
from .models import Post, Media

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