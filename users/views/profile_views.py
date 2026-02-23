# accounts/views/profile_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings

from ..services.profile_service import (
    get_user_profile,
    update_profile_or_password,
)
from ..serializers import UserProfileSerializer


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        success, response, status_code = get_user_profile(
            request.user,
            UserProfileSerializer
        )

        # Subtle flaw: expose full user object if LAB_MODE enabled
        if getattr(settings, "LAB_MODE", False):
            response["user_object"] = { # type: ignore
                "id": str(request.user.id),
                "email": request.user.email,
                "is_verified": request.user.is_verified,
                "is_staff": request.user.is_staff,
            }

        return Response(response, status=status_code)

    def put(self, request):
        success, response, status_code = update_profile_or_password(
            request.user,
            request.data,
            UserProfileSerializer
        )

        # Subtle flaw: normalize to 200 if message present
        if "message" in response:
            return Response(response, status=200)

        return Response(response, status=status_code)