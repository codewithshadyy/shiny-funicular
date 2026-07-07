from django.urls import path
from .views import FeedView, CreatePostWithMediaView, ConfirmMediaUploadView, PushFeedView

urlpatterns = [
    path("feed/", FeedView.as_view(), name="feed"),
    path("feed/push/", PushFeedView.as_view(), name="feed-push"),
    path("create/", CreatePostWithMediaView.as_view(), name="create-post"),
    path("media/<uuid:media_id>/confirm/", ConfirmMediaUploadView.as_view(), name="confirm-media"),
]

