from django.db import models

from django.conf import settings

class Follow(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="following")
    following = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="followers")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "following"], name="unique_pair_follow"
            ),
            models.CheckConstraint(
                condition=~models.Q(follower=models.F("following")),
                name="cannot follow itself"
            )
    
        ]
        
        indexes = [
            models.Index(fields=["follower", "-created_at"]),
            
            models.Index(fields=["following", "-created_at"])
        ]
        
    def __str__(self):
        return f"{self.follower.handle} -> {self.following.handle}"    
