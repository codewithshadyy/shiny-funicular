from django.urls import path
from .views import FeedView, CreatePostWithMediaView

urlpatterns = [
    path("feed/", FeedView.as_view(), name="feed"),
    path("create/", CreatePostWithMediaView.as_view(), name="create-post"),
]

