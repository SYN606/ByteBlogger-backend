from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from .models import User, OTPRequest
from .serializers import UserSerializer
from .otp import generate_otp, send_otp_email


class TokenRefreshView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh_token")

        if not refresh_token:
            raise AuthenticationFailed("Refresh token is missing.")

        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = refresh.access_token
            new_refresh_token = RefreshToken.for_user(refresh.user)
            return Response({
                "message": "Tokens refreshed successfully.",
                "access_token": str(new_access_token),
                "refresh_token": str(new_refresh_token),
            })
        except Exception as e:
            raise AuthenticationFailed("Invalid refresh token.")


class UserRegisterView(APIView):

    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            otp = generate_otp()
            OTPRequest.objects.create(user=user, otp=otp)
            send_otp_email(user.email, otp)

            return Response(
                {
                    "user_id":
                    user.id,
                    "message":
                    "User created. Please check your email for OTP verification."
                },
                status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email and password are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)

        if user is None:
            return Response({"error": "Invalid credentials."},
                            status=status.HTTP_400_BAD_REQUEST)

        if not user.is_verified:
            otp_cached = OTPRequest.objects.filter(
                user_id=user.id).order_by("-request_time").first()
            if not otp_cached:
                otp = generate_otp()
                OTPRequest.objects.create(user=user, otp=otp)
                send_otp_email(user.email, otp)

            return Response(
                {
                    "message":
                    "User not verified. Please check your email for OTP verification."
                },
                status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Login successful.",
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        })


class OTPVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_id = request.data.get("user_id")
        otp_input = request.data.get("otp")

        if not user_id or not otp_input:
            return Response({"error": "user_id and OTP are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        otp_request = OTPRequest.objects.filter(
            user_id=user_id).order_by("-request_time").first()

        if not otp_request:
            return Response({"error": "OTP request not found."},
                            status=status.HTTP_400_BAD_REQUEST)

        if otp_request.is_expired():
            return Response({"error": "OTP expired."},
                            status=status.HTTP_400_BAD_REQUEST)

        if otp_input != otp_request.otp:
            return Response({"error": "Incorrect OTP."},
                            status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, id=user_id)
        user.is_verified = True
        user.save()
        otp_request.delete()

        return Response(
            {
                "message": "User verified successfully.",
                "user_id": user.id,
                "is_verified": user.is_verified
            },
            status=status.HTTP_200_OK)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_serializer = UserSerializer(user)
        return Response({"data": user_serializer.data},
                        status=status.HTTP_200_OK)

    def put(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if old_password and new_password:
            if not user.check_password(old_password):
                return Response({"error": "Old password is incorrect."},
                                status=status.HTTP_400_BAD_REQUEST)
            user.set_password(new_password)
            user.save()
            return Response({"message": "Password updated successfully."},
                            status=status.HTTP_200_OK)

        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully."},
                            status=status.HTTP_200_OK)

        return Response({"error": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response({"detail": "Refresh token is required."},
                                status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            if not token.check_blacklist():
                token.blacklist()

            return Response({"detail": "Successfully logged out."},
                            status=status.HTTP_200_OK)
        except TokenError as e:
            return Response({"detail": str(e)},
                            status=status.HTTP_400_BAD_REQUEST)
