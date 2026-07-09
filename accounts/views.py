from django.shortcuts import render

from .serializers import RegisterSerializer
from rest_framework.viewsets import ModelViewSet
from .models import Creator
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .utils import account_token_generator
from .tasks import send_password_reset_email
from .throttles import LoginRateThrottle, PasswordResetRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView

class RegisterView(ModelViewSet):
    
    queryset = Creator.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    
    
class ThrottledTokenObtainPairView(TokenObtainPairView):
    throttle_classes = [LoginRateThrottle]   
    throttle_scope = "login" 
    
    
class LogoutView(APIView):
    
    permission_classes = [AllowAny]
    
    
    def post(self, request):
        refresh_token = request.data.get("refresh")
        
        if not refresh_token:
            return Response({"error": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            
        except TokenError:
            return Response({"error": "Invalid or already blacklisted token"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)    
        


class RequestPasswordResetView(APIView):
    permission_classes = [AllowAny]
    
    throttle_classes = [PasswordResetRateThrottle]
    throttle_scope = "password_reset"

    def post(self, request):
        handle = request.data.get("handle", "")

        generic_response = Response(
            {"message": "If an account with that handle exists, a reset link has been sent."},
            status=status.HTTP_200_OK,
        )

        try:
            user = Creator.objects.get(handle=handle)
        except Creator.DoesNotExist:
            return generic_response

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_token_generator.make_token(user)

        send_password_reset_email.delay(user.email, user.handle, uid, token)

        return generic_response


class ConfirmPasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        uid = request.data.get("uid")
        token = request.data.get("token")
        new_password = request.data.get("new_password")

        if not all([uid, token, new_password]):
            return Response(
                {"error": "uid, token, and new_password are all required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = Creator.objects.get(pk=user_id)
        except (Creator.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response({"error": "Invalid reset link"}, status=status.HTTP_400_BAD_REQUEST)

        if not account_token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired reset token"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(new_password, user=user)
        except ValidationError as e:
            return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)    