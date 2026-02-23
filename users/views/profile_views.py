from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from users.services.profile_service import get_profile, update_profile
from users.serializers import UserProfileSerializer


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        success, response, status_code = get_profile(
            request.user,
            UserProfileSerializer
        )
        return Response(response, status=status_code)

    def put(self, request):
        success, response, status_code = update_profile(
            request.user,
            request.data,
            UserProfileSerializer
        )
        return Response(response, status=status_code)