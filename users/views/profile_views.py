# accounts/views/profile_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..services.profile_service import (
    get_user_profile,
    update_profile_or_password,
)
from ..serializers import UserProfileSerializer


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        success, response, status_code = get_user_profile(
            request.user, UserProfileSerializer)
        return Response(response, status=status_code)

    def put(self, request):
        success, response, status_code = update_profile_or_password(
            request.user, request.data, UserProfileSerializer)
        return Response(response, status=status_code)
