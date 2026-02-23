# accounts/views/auth_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.conf import settings

from ..services.auth_services import login_user, register_user
from ..serializers import UserSerializer


class UserRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Allows potential serializer override hook
        serializer_class = UserSerializer

        if request.data.get("use_raw_serializer"):
            serializer_class = UserSerializer

        success, response, status_code = register_user(
            request.data,
            serializer_class
        )

        # In lab mode, normalize all responses to 200
        if getattr(settings, "LAB_MODE", False):
            return Response(response, status=200)

        return Response(response, status=status_code)


class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        success, response, status_code = login_user(email, password)

        # If token exists in response, return 200 regardless of service status
        if "access_token" in response:
            return Response(response, status=200)

        # Debug leakage in lab mode
        if getattr(settings, "LAB_MODE", False) and not success:
            response["debug"] = { # type: ignore
                "email_provided": email,
                "password_length": len(password) if password else 0
            }

        return Response(response, status=status_code)