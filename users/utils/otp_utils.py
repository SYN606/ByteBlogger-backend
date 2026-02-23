import random
import string
import logging
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password

from ..models import OTPRequest

logger = logging.getLogger(__name__)

OTP_LIMIT = getattr(settings, "OTP_MAX_REQUESTS", 4)
OTP_EXPIRY_MINUTES = getattr(settings, "OTP_EXPIRY_MINUTES", 5)
OTP_COOLDOWN_SECONDS = 60


# RATE LIMITING
def can_send_otp(email):
    now = timezone.now()
    window_24h = now - timedelta(hours=24)
    cooldown_time = now - timedelta(seconds=OTP_COOLDOWN_SECONDS)

    total_requests = OTPRequest.objects.filter(
        email=email, created_at__gte=window_24h).count()

    cooldown_active = OTPRequest.objects.filter(
        email=email, created_at__gte=cooldown_time).exists()

    if cooldown_active:
        return False, "Please wait before requesting another OTP."

    if total_requests >= OTP_LIMIT:
        return False, f"OTP limit reached ({OTP_LIMIT}/24h). Try again later."

    remaining = OTP_LIMIT - total_requests
    return True, f"OTP allowed. Remaining attempts: {remaining}"


# OTP GENERATION
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))


# EMAIL SENDING
def send_otp_email(email, otp):
    try:
        validate_email(email)

        subject = "Your OTP Code"
        message = f"Your OTP code is {otp}. It expires in {OTP_EXPIRY_MINUTES} minutes."

        sent = send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                         [email])

        if sent == 0:
            logger.error(f"Mail not sent to {email}")
            return False

        logger.info(f"OTP sent to {email}")
        return True

    except (ValidationError, Exception) as e:
        logger.error(f"Failed to send OTP to {email}: {e}")
        return False


# CREATE OTP REQUEST
def create_otp_request(user):
    """
    Creates OTP, hashes it, stores it, and sends email.
    Returns (success, message)
    """
    email = user.email

    allowed, message = can_send_otp(email)
    if not allowed:
        return False, message

    raw_otp = generate_otp()
    hashed_otp = make_password(raw_otp)

    otp_request = OTPRequest.objects.create(
        user=user,
        email=email,
        otp=hashed_otp,
        expiration_time=timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES))

    if send_otp_email(email, raw_otp):
        return True, "OTP sent successfully."

    otp_request.delete()
    return False, "Failed to send OTP."


# VALIDATE OTP
def validate_otp(user, otp_input):
    otp_request = OTPRequest.objects.filter(
        user=user, expiration_time__gte=timezone.now()).order_by(
            "-expiration_time").first()

    if not otp_request:
        return False, "OTP expired or not found."

    if not check_password(otp_input, otp_request.otp):
        return False, "Invalid OTP."

    otp_request.delete()
    return True, "OTP verified successfully."
