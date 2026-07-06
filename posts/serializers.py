from rest_framework import serializers
from .models import Post, Media

class MediaSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Media
        fields = [
            "id", "media_type", "storage_key", "processing_status",
            "duration_seconds", "thumbnail_key", "width", "height", "order",
        ]

        