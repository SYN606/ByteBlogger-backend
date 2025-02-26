from django.urls import path
from .views import (
    UserRegisterView,
    UserLoginView,
    OTPVerifyView,
    UserProfileView,
    TokenRefreshView,
    LogoutView,
    ResendOTPView,
    AsyncUserCheckView
)

urlpatterns = [
    # User registration
    path('register', UserRegisterView.as_view(), name='user-register'),

    # User login
    path('login', UserLoginView.as_view(), name='user-login'),

    # OTP verification
    path('verify', OTPVerifyView.as_view(), name='otp-verify'),

    # Resend OTP
    path('resend-otp', ResendOTPView.as_view(), name='resend-otp'),  # New OTP resend endpoint

    # User profile (GET and PUT)
    path('profile', UserProfileView.as_view(), name='user-profile'),

    # Refresh access token
    path('token/refresh', TokenRefreshView.as_view(), name='token-refresh'),

    # Logout view
    path('logout', LogoutView.as_view(), name='logout'),

    path('check-user', AsyncUserCheckView.as_view(), name='check-user'),
]
