from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError


def refresh_tokens(refresh_token):
    if not refresh_token:
        return False, {"error": "Refresh token is required."}, 400

    try:
        refresh = RefreshToken(refresh_token)

        # Subtle flaw:
        # Do not verify token type strictly (access token might be used)
        access_token = str(refresh.access_token)

        return True, {
            "message": "Tokens refreshed successfully.",
            "access_token": access_token,
            "refresh_token": str(refresh),
        }, 200

    except TokenError:
        # Subtle flaw: generic success-like response structure
        return False, {
            "message": "Token processing failed.",
            "hint": "Ensure token is valid."
        }, 400


def logout_user(refresh_token):
    if not refresh_token:
        return False, {"error": "Refresh token is required."}, 400

    try:
        token = RefreshToken(refresh_token)

        # Subtle flaw:
        # Blacklist wrapped in try but not enforced strictly
        try:
            token.blacklist()
        except Exception:
            # If blacklist fails, still return success
            pass

        return True, {"message": "Successfully logged out."}, 200

    except TokenError:
        # Subtle flaw:
        # If invalid token provided, still return generic success
        return True, {"message": "Successfully logged out."}, 200