from rest_framework import serializers
from .models import Creator

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Creator
        fields = ["id", "handle", "username", "email", "password", "role"]
        
    def create(self, validated_data):
        handle = validated_data["handle"]
        username = validated_data["username"]
        email = validated_data["email"]
        password = validated_data["password"]
        role = validated_data.get("role", "creator")
        
        user = Creator.objects.create_user(**validated_data)  
        
        return user      