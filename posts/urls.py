from django.urls import path
from .views import FeedView, CreatePostWithMediaView, ConfirmMediaUploadView, PushFeedView, ToggleLikeView, CommentListCreateView, NotificationListView, MarkNotificationReadView

urlpatterns = [
    
    path("feed/", FeedView.as_view(), name="feed"),
    path("feed/push/", PushFeedView.as_view(), name="feed-push"),
    path("create/", CreatePostWithMediaView.as_view(), name="create-post"),
    path("media/<uuid:media_id>/confirm/", ConfirmMediaUploadView.as_view(), name="confirm-media"),
    path("<uuid:post_id>/like/", ToggleLikeView.as_view(), name="toggle-like"),
    path("<uuid:post_id>/comments/", CommentListCreateView.as_view(), name="post-comments"),
    path("notifications/", NotificationListView.as_view(), name="notifications"),
    path("notifications/<uuid:notification_id>/read/", MarkNotificationReadView.as_view(), name="mark-notification-read")
    
]

