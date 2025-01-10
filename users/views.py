from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from .models import User
from .serializers import UserSerializer
from .otp import generate_otp, send_otp_email
from django.utils import timezone
from datetime import timedelta


# User Registration View
class UserRegisterView(APIView):

    def post(self, request):
        data = request.data
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not username or not email or not password:
            return Response({"error": "All fields are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email is already registered."},
                            status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username,
                                        email=email,
                                        password=password)
        user_id = user.id

        # Generate OTP and send to email
        otp = generate_otp()
        cache.set(f'otp_{user_id}', otp,
                  timeout=300)  # OTP valid for 5 minutes
        send_otp_email(email, otp)

        return Response(
            {
                "user_id":
                user_id,
                "message":
                "User created. Please check your email for OTP verification."
            },
            status=status.HTTP_201_CREATED)


# OTP Verification View
class OTPVerifyView(APIView):

    def post(self, request, user_id):
        otp = request.data.get('otp')
        user = get_object_or_404(User, id=user_id)

        # Retrieve OTP from cache
        cached_otp = cache.get(f'otp_{user_id}')

        if not cached_otp:
            return Response({"error": "OTP has expired."},
                            status=status.HTTP_400_BAD_REQUEST)

        if otp == cached_otp:
            user.is_verified = True
            user.save()

            # Delete OTP after successful verification
            cache.delete(f'otp_{user_id}')

            # Create access and refresh tokens
            refresh = RefreshToken.for_user(user)
            response = Response({
                "message": "OTP verified successfully.",
                "user_id": user.id,
                "is_verified": user.is_verified,
            })
            response.set_cookie('access',
                                str(refresh.access_token),
                                httponly=True)
            response.set_cookie('refresh', str(refresh), httponly=True)
            return response

        return Response({"error": "Invalid OTP."},
                        status=status.HTTP_400_BAD_REQUEST)


# User Login View
class UserLoginView(APIView):

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"error": "Email and password are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Authenticate the user
        user = authenticate(request, email=email, password=password)

        if user is None:
            return Response({"error": "Invalid credentials."},
                            status=status.HTTP_400_BAD_REQUEST)

        if not user.is_verified:
            # Generate OTP and send to email for verification
            otp = generate_otp()
            cache.set(f'otp_{user.id}', otp, timeout=300)
            send_otp_email(user.email, otp)

            return Response(
                {
                    "message":
                    "User not verified. Please check your email for OTP verification."
                },
                status=status.HTTP_400_BAD_REQUEST)

        # If user is verified, generate JWT tokens
        refresh = RefreshToken.for_user(user)
        response = Response({
            "message": "Login successful.",
        })
        response.set_cookie('access', str(refresh.access_token), httponly=True)
        response.set_cookie('refresh', str(refresh), httponly=True)
        return response
