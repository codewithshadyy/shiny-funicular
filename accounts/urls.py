from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView
router = DefaultRouter()
router.register(r"register", RegisterView, basename="register")
# router.register(r"login", TokenObtainPairView.as_view(), basename="login")


urlpatterns = [
    path("", include(router.urls)),
    path("login/", TokenObtainPairView.as_view())
]
