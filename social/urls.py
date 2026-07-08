from django.urls import path
from .views import ToggleFollowView

urlpatterns = [
    path("<int:user_id>/follow/", ToggleFollowView.as_view(), name="toggle-follow"),
]