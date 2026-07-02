from django.db import models


from django.contrib.auth.models import AbstractUser

class Creator(AbstractUser):
    
    ROLE_CHOICES = (
        ("creator","cre"),
        ("moderator", "mod")
    )
    role = models.CharField(ROLE_CHOICES=ROLE_CHOICES, default="creator")
    handle = models.CharField(unique=True)
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    USERNAME_FIELD = "handle"
    REQUIRED_FIELDS = ['username']
    
    
    def __str__(self):
        return self.handle
    
    
