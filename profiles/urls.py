
from django.urls import path
from .views import AvatarUploadRequestView, AvatarConfirmView, UserSearchSerializer, ProfileDetailView, UserPostsView, UserSearchView

urlpatterns = [
    path("search/", UserSearchView.as_view(), name="user-search"),
    path("avatar/upload/", AvatarUploadRequestView.as_view(), name="avatar-upload"),
    path("avatar/confirm/", AvatarConfirmView.as_view(), name="avatar-confirm"),
    path("<str:handle>/", ProfileDetailView.as_view(), name="profile-detail"),
    path("<str:handle>/posts/", UserPostsView.as_view(), name="user-posts"),
]