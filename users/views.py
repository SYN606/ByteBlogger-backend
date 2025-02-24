# from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from .models import User, OTPRequest, UserProfile
from .serializers import UserSerializer, UserProfileSerializer
from .otp import generate_otp, send_otp_email


# Token Refresh View
class TokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response({"error": "Refresh token is required."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            return Response({
                "message": "Tokens refreshed successfully.",
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
            })
        except Exception:
            return Response({"error": "Invalid refresh token."},
                            status=status.HTTP_400_BAD_REQUEST)


# User Registration View
class UserRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            otp = generate_otp()
            OTPRequest.objects.create(user=user, otp=otp)
            response = send_otp_email(user.email, otp)

            return Response(
                {
                    "user_id":
                    user.id,
                    "response":
                    response, # will return true if otp is sent on correct address 
                },
                status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# User Login View
class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email and password are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)
        if not user:
            return Response({"error": "Invalid credentials."},
                            status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_verified:  # type: ignore
            otp = generate_otp()
            OTPRequest.objects.create(user=user, otp=otp)
            send_otp_email(user.email, otp)
            return Response(
                {
                    "message":
                    "Account not verified. Check your email for OTP verification."
                },
                status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "message": "Login successful.",
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
            },
            status=status.HTTP_200_OK)


# OTP Verification View
class OTPVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_id = request.data.get("user_id")
        otp_input = request.data.get("otp")

        if not user_id or not otp_input:
            return Response({"error": "User ID and OTP are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        otp_request = OTPRequest.objects.filter(
            user_id=user_id).order_by("-request_time").first()
        if not otp_request:
            return Response({"error": "OTP request not found."},
                            status=status.HTTP_404_NOT_FOUND)

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


# User Profile View
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # Ensure the UserProfile is created if it doesn't exist
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

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

        user_profile = get_object_or_404(UserProfile, user=user)
        serializer = UserProfileSerializer(user_profile,
                                           data=request.data,
                                           partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully."},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Logout View
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response({"error": "Refresh token is required."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out."},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)},
                            status=status.HTTP_400_BAD_REQUEST)
