from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from users.services.otp_service import verify_otp, resend_otp


class OTPVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        success, response, status_code = verify_otp(
            request.data.get("user_id"),
            request.data.get("otp"),
        )
        return Response(response, status=status_code)


class ResendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        success, response, status_code = resend_otp(
            request.data.get("user_id")
        )
        return Response(response, status=status_code)