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
    permission_classes = [IsAuthenticated]  # User must be authenticated

    def post(self, request):
        refresh_token = request.COOKIES.get(
            'refresh')  # Get refresh token from cookies

        if not refresh_token:
            raise AuthenticationFailed('Refresh token is missing.')

        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = refresh.access_token
            new_refresh_token = RefreshToken.for_user(refresh.user)
            response = Response({
                "message": "Tokens refreshed successfully.",
                "access_token": str(new_access_token),
                "refresh_token": str(new_refresh_token),
            })
            response.set_cookie('access', str(new_access_token), httponly=True)
            response.set_cookie('refresh',
                                str(new_refresh_token),
                                httponly=True)

            return response
        except Exception as e:
            raise AuthenticationFailed('Invalid refresh token.')


# User Registration View
class UserRegisterView(APIView):

    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            # Save user if serializer is valid
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
            # Check if OTP is already sent and if the user is verified
            otp_cached = OTPRequest.objects.filter(
                user_id=user.id).order_by('-request_time').first()

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

        # If user is verified, generate JWT tokens
        refresh = RefreshToken.for_user(user)
        response = Response({
            "message": "Login successful.",
        })
        response.set_cookie('access', str(refresh.access_token), httponly=True)
        response.set_cookie('refresh', str(refresh), httponly=True)
        return response


# OTP Verification View
class OTPVerifyView(APIView):
    permission_classes = [AllowAny]  # Allow public access to OTP verification

    def post(self, request):
        user_id = request.data.get("user_id")
        otp_input = request.data.get("otp")

        if not user_id or not otp_input:
            return Response({"error": "user_id and OTP are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Retrieve OTP request from the database
        otp_request = OTPRequest.objects.filter(
            user_id=user_id).order_by('-request_time').first()

        if not otp_request:
            return Response({"error": "OTP request not found."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check if OTP has expired
        if otp_request.is_expired():
            return Response({"error": "OTP expired."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Validate the OTP
        if otp_input != otp_request.otp:
            return Response({"error": "Incorrect OTP."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Mark the user as verified
        user = get_object_or_404(User, id=user_id)
        user.is_verified = True
        user.save()

        # Delete OTP from the database after successful verification
        otp_request.delete()

        return Response(
            {
                "message": "User verified successfully.",
                "user_id": user.id,
                "is_verified": user.is_verified
            },
            status=status.HTTP_200_OK)


# Profile View (GET and PUT)
class UserProfileView(APIView):

    def get(self, request):
        user_id = request.data.get("user_id")
        access_token = request.COOKIES.get("access")
        refresh_token = request.COOKIES.get("refresh")

        if not user_id or not access_token or not refresh_token:
            return Response(
                {
                    "error":
                    "user_id, access_token, and refresh_token are required."
                },
                status=status.HTTP_400_BAD_REQUEST)

        try:
            # Validate the access token
            RefreshToken(access_token)
        except (TokenError, InvalidToken):
            return Response({"error": "Invalid or expired access token."},
                            status=status.HTTP_401_UNAUTHORIZED)

        user = get_object_or_404(User, id=user_id)
        user_serializer = UserSerializer(user)

        return Response({"data": user_serializer.data},
                        status=status.HTTP_200_OK)

    def put(self, request):
        user_id = request.data.get("user_id")
        access_token = request.COOKIES.get("access")
        refresh_token = request.COOKIES.get("refresh")
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not user_id or not access_token or not refresh_token:
            return Response(
                {
                    "error":
                    "user_id, access_token, and refresh_token are required."
                },
                status=status.HTTP_400_BAD_REQUEST)

        try:
            # Validate the access token
            RefreshToken(access_token)
        except (TokenError, InvalidToken):
            return Response({"error": "Invalid or expired access token."},
                            status=status.HTTP_401_UNAUTHORIZED)

        user = get_object_or_404(User, id=user_id)

        if old_password and new_password:
            # Authenticate user with old password to verify identity
            if not authenticate(
                    request, username=user.email, password=old_password):
                return Response({"error": "Old password is incorrect."},
                                status=status.HTTP_400_BAD_REQUEST)
            user.set_password(new_password)  # Update the password
            user.save()

            return Response(
                {"data": {
                    "message": "Password updated successfully."
                }},
                status=status.HTTP_200_OK)

        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            # If email is updated, trigger OTP verification for the old email
            if 'email' in request.data:
                old_email = user.email
                new_email = request.data['email']

                # Generate OTP for the old email to verify
                otp = generate_otp()
                OTPRequest.objects.create(user=user, email=old_email, otp=otp)

                # Send the OTP to the old email address
                send_otp_email(old_email, otp)

                return Response(
                    {
                        "data": {
                            "message":
                            f"Please verify your new email: {new_email} via OTP sent to {old_email}."
                        }
                    },
                    status=status.HTTP_200_OK)

            # If no email change, save the updated profile
            serializer.save()
            return Response(
                {"data": {
                    "message": "Profile updated successfully."
                }},
                status=status.HTTP_200_OK)

        return Response({"error": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Extract the refresh token from cookies
            refresh_token = request.COOKIES.get('refresh_token')

            if not refresh_token:
                return JsonResponse(
                    {"detail": "Refresh token is missing in cookies."},
                    status=status.HTTP_400_BAD_REQUEST)

            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()

            # Remove the refresh token cookie from the client's browser
            response = JsonResponse({"detail": "Successfully logged out."},
                                    status=status.HTTP_200_OK)
            response.delete_cookie(
                'refresh_token')  # Delete the refresh token cookie
            response.delete_cookie(
                'access_token'
            )  # Optionally, delete the access token cookie as well

            return response
        except Exception as e:
            return JsonResponse({"detail": str(e)},
                                status=status.HTTP_400_BAD_REQUEST)
