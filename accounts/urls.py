from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, LogoutView, RequestPasswordResetView, ConfirmPasswordResetView, ThrottledTokenObtainPairView
router = DefaultRouter()
router.register(r"register", RegisterView, basename="register")
# router.register(r"login", TokenObtainPairView.as_view(), basename="login")


urlpatterns = [
    path("", include(router.urls)),
    path("token/", ThrottledTokenObtainPairView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),
    path("logout/", LogoutView.as_view(), name="logout"),
     path("password-reset/", RequestPasswordResetView.as_view(), name="password-reset-request"),
    path("password-reset/confirm/", ConfirmPasswordResetView.as_view(), name="password-reset-confirm"),
    
]
