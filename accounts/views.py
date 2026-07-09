from django.shortcuts import render

from .serializers import RegisterSerializer
from rest_framework.viewsets import ModelViewSet
from .models import Creator
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class RegisterView(ModelViewSet):
    queryset = Creator.objects.all()
    serializer_class = RegisterSerializer
    
    
    
    
class LogoutView(APIView):
    
    
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
        
    