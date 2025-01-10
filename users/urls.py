from django.urls import path
from .views import UserRegisterView, UserLoginView, OTPVerifyView, UserProfileView, TokenRefreshView, LogoutView

urlpatterns = [
    # User registration
    path('register/', UserRegisterView.as_view(), name='user-register'),

    # User login
    path('login/', UserLoginView.as_view(), name='user-login'),

    # OTP verification
    path('verify/', OTPVerifyView.as_view(), name='otp-verify'),

    # User profile (GET and PUT)
    path('profile/', UserProfileView.as_view(), name='user-profile'),

    # for refrehsing access tokens
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # logout view
    path('logout/', LogoutView.as_view(), name='logout'),
]
