from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from ..services.token_service import refresh_tokens, logout_user


class TokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        success, response, status_code = refresh_tokens(
            request.data.get("refresh_token"))
        return Response(response, status=status_code)


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        success, response, status_code = logout_user(
            request.data.get("refresh_token"))
        return Response(response, status=status_code)
