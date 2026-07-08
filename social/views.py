from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from accounts.models import Creator
from .models import Follow


class ToggleFollowView(APIView):
    def post(self, request, user_id):
        target_user = get_object_or_404(Creator, id=user_id)

        if target_user.id == request.user.id:
            return Response({"error": "Cannot follow yourself"}, status=status.HTTP_400_BAD_REQUEST)

        follow, created = Follow.objects.get_or_create(follower=request.user, following=target_user)

        if created:
           
            from posts.models import Notification
            Notification.objects.create(
                recipient=target_user,
                actor=request.user,
                notification_type="follow",
            )

        return Response({"following": True}, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def delete(self, request, user_id):
        target_user = get_object_or_404(Creator, id=user_id)
        Follow.objects.filter(follower=request.user, following=target_user).delete()
        return Response({"following": False}, status=status.HTTP_200_OK)
