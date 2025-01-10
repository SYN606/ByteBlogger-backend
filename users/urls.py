from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import UserRegisterView, OTPVerifyView, UserLoginView

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='user_register'),
    path('<int:user_id>/verify/', OTPVerifyView.as_view(), name='otp_verify'),
    path('login/', UserLoginView.as_view(), name='user_login'),
]

# Optional: Add format suffixes (e.g., .json, .api)
urlpatterns = format_suffix_patterns(urlpatterns)
