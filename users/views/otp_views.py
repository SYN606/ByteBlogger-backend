from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.conf import settings

from ..services.otp_service import verify_otp, resend_otp


class OTPVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        success, response, status_code = verify_otp(
            request.data.get("user_id"),
            request.data.get("otp")
        )

        # Subtle flaw: normalize status to 200 in lab mode
        if getattr(settings, "LAB_MODE", False):
            return Response(response, status=200)

        return Response(response, status=status_code)


class ResendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        success, response, status_code = resend_otp(
            request.data.get("user_id")
        )

        # Subtle flaw: always return 200 if message exists
        if "message" in response:
            return Response(response, status=200)

        return Response(response, status=status_code)