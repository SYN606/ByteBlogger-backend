from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from users.services.auth_service import register_user, login_user


class UserRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        success, response, status_code = register_user(request.data)
        return Response(response, status=status_code)


class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        success, response, status_code = login_user(
            request.data.get("email"),
            request.data.get("password"),
        )
        return Response(response, status=status_code)