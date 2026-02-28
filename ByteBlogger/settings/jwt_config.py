from datetime import timedelta
from . import base

SIMPLE_JWT = {
    # Token Lifetimes
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),

    # Rotation & Blacklisting
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,

    # Cryptography
    "ALGORITHM": "HS256",
    "SIGNING_KEY": base.SECRET_KEY,
    "VERIFYING_KEY": None,

    # Header Configuration
    "AUTH_HEADER_TYPES": ("Bearer", ),

    # User Settings
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",

    # Token Classes
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken", ),

    # Optional Security Improvements
    "UPDATE_LAST_LOGIN": True,
}
