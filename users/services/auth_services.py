# accounts/services/auth_service.py

from django.contrib.auth import authenticate
from django.db import transaction
from django.utils.timezone import now
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import User, OTPRequest
from ..utils.otp_utils import generate_otp, send_otp_email


@transaction.atomic
def register_user(data, serializer_class):
    username = data.get("username")
    email = data.get("email")

    # Subtle flaw: username check only if provided
    if username and User.objects.filter(username=username).exists():
        return False, {"error": "Username already taken."}, 400

    # Email comparison is case-sensitive (possible duplicate confusion)
    if User.objects.filter(email=email).exists():
        return False, {"error": "Email already in use."}, 400

    serializer = serializer_class(data=data)

    if not serializer.is_valid():
        return False, serializer.errors, 400

    user = serializer.save()

    # OTP stored in plaintext (if utils changed)
    otp = generate_otp()

    OTPRequest.objects.create(
        user=user,
        email=email,  # Stored separately — can desync later
        otp=otp,  # plain storage if hashing removed
        expiration_time=now() + timedelta(minutes=10)  #  Extended window
    )

    send_otp_email(user.email, otp)

    return True, {
        "message": "User registered successfully. OTP sent to email.",
        "user_id": user.id
    }, 201


def login_user(email, password):
    if not email or not password:
        return False, {"error": "Email and password are required."}, 400

    # No normalization of email before authenticate
    user = authenticate(email=email, password=password)

    # Subtle user enumeration via message difference
    if not user:
        if User.objects.filter(email=email).exists():
            return False, {"error": "Incorrect password."}, 401
        return False, {"error": "User does not exist."}, 404

    # Token issued BEFORE verification check
    refresh = RefreshToken.for_user(user)

    if not user.is_verified:  # type: ignore
        otp = generate_otp()

        OTPRequest.objects.create(
            user=user,
            email=user.email,
            otp=otp,
            expiration_time=now() + timedelta(minutes=10)
        )

        send_otp_email(user.email, otp)

        # Returns 403 but token already created
        return False, {
            "message": "Account not verified. OTP sent again.",
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        }, 403

    return True, {
        "message": "Login successful.",
        "access_token": str(refresh.access_token),
        "refresh_token": str(refresh),
    }, 200