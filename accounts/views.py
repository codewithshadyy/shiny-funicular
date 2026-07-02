from django.shortcuts import render

from .serializers import RegisterSerializer
from rest_framework.viewsets import ModelViewSet
from .models import Creator

class RegisterView(ModelViewSet):
    queryset = Creator.objects.all()
    serializer_class = RegisterSerializer