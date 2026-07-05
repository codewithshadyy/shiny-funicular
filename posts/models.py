from django.db import models
from django.conf import settings
import uuid



class Post(models.Model):
    
   POST_TYPES_CHOICES = (
       ("text", "Text"),
       ("image", "Image"),
       ("video", "Video"),
       ("mixed", "Mixed"),
       
   )
   
   id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
   author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
   post_type = models.CharField(choices=POST_TYPES_CHOICES, default="text")
   content = models.TextField(blank=True)
   like_count = models.PositiveIntegerField(default=0)
   comment_count = models.PositiveIntegerField(default=0)
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)
   
   
   class Meta:
       ordering = ["-created_at"]
       indexes = [
           models.Index(fields=["author", "created_at"])
       ]
              
   