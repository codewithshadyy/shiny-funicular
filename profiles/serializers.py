from rest_framework import serializers
from .models import Profile
from media_storage.utils import get_presigned_get_url


class ProfileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="user.id", read_only=True)
    handle = serializers.CharField(source="user.handle", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    avatar_url = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    is_self = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "handle", "username", "bio", "avatar_url", "location", "website",
            "follower_count", "following_count", "post_count",
            "is_following", "is_self",
        ]

    def get_avatar_url(self, obj):
        return get_presigned_get_url(obj.avatar_key) if obj.avatar_key else None

    def get_is_following(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        from social.models import Follow
        return Follow.objects.filter(follower=request.user, following=obj.user).exists()

    def get_is_self(self, obj):
        request = self.context.get("request")
        return bool(request and request.user.is_authenticated and request.user.id == obj.user_id)


class UserSearchSerializer(serializers.Serializer):
  
    handle = serializers.CharField()
    username = serializers.CharField()
    avatar_url = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    def get_avatar_url(self, obj):
        avatar_key = getattr(obj.profile, "avatar_key", "") if hasattr(obj, "profile") else ""
        return get_presigned_get_url(avatar_key) if avatar_key else None

    def get_is_following(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        from social.models import Follow
        return Follow.objects.filter(follower=request.user, following=obj).exists()