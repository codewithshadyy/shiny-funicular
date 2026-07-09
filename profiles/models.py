from django.db import models

# profiles/models.py
from django.db import models
from django.conf import settings
import uuid


class Profile(models.Model):
  

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        primary_key=True,
    )
    bio = models.TextField(max_length=280, blank=True)
    avatar_key = models.CharField(max_length=500, blank=True)  
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)

   
    follower_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)
    post_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile: {self.user.handle}"
