from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User
from users.serializers import UserSerializer
from users.utils.otp import create_otp_request


@transaction.atomic
def register_user(data):
    serializer = UserSerializer(data=data)

    if not serializer.is_valid():
        return False, serializer.errors, 400

    user = serializer.save()

    success, message = create_otp_request(user)
    if not success:
        return False, {"error": message}, 400

    return True, {"message": "Registration successful. OTP sent."}, 201


def login_user(email, password):
    if not email or not password:
        return False, {"error": "Email and password are required."}, 400

    user = authenticate(email=email.lower(), password=password)

    if not user:
        return False, {"error": "Invalid credentials."}, 401

    if not user.is_verified: # type: ignore
        create_otp_request(user)
        return False, {"error": "Account not verified."}, 403

    refresh = RefreshToken.for_user(user)

    return True, {
        "access_token": str(refresh.access_token),
        "refresh_token": str(refresh),
    }, 200
