from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError


def refresh_tokens(refresh_token):
    if not refresh_token:
        return False, {"error": "Refresh token required."}, 400

    try:
        refresh = RefreshToken(refresh_token)

        return True, {
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        }, 200

    except TokenError:
        return False, {"error": "Invalid or expired refresh token."}, 400


def logout_user(refresh_token):
    if not refresh_token:
        return False, {"error": "Refresh token required."}, 400

    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        return True, {"message": "Logged out successfully."}, 200

    except TokenError:
        return False, {"error": "Invalid or expired refresh token."}, 400
