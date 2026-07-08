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
       
   def __str__(self):
        return f"{self.author.handle}: {self.content[:30]}"   
 
class Media(models.Model):
    
     MEDIA_TYPE_CHOICES = (
        ("image", "Image"),
        ("video", "Video"),
    )

     PROCESSING_STATUS_CHOICES = (
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("ready", "Ready"),
        ("failed", "Failed"),
    )
     
     
     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
     post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="media_items")
     media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)

     storage_key = models.CharField(max_length=500)

     processing_status = models.CharField(
        max_length=20, choices=PROCESSING_STATUS_CHOICES, default="pending"
    )

     duration_seconds = models.PositiveIntegerField(null=True, blank=True)
     thumbnail_key = models.CharField(max_length=500, blank=True)
     width = models.PositiveIntegerField(null=True, blank=True)
     height = models.PositiveIntegerField(null=True, blank=True)

     order = models.PositiveSmallIntegerField(default=0)
     created_at = models.DateTimeField(auto_now_add=True)

     class Meta:
        ordering = ["order"]

     def __str__(self):
        return f"{self.media_type} for post {self.post_id}"
                 
class Like(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["post", "user"], name="unique_like_per_user")
        ] 
        
        indexes = [
            models.Index(fields=["post", "user"])
            
        ]  
        
    def __str__(self):
        
        return f"{self.user.handle} likes {self.post_id}"
    
        
        