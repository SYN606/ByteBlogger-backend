import random
import string
import logging
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
from users.models import OTPRequest  # Assuming this is your OTP model

logger = logging.getLogger(__name__)

# Default OTP limit (if not in settings)
OTP_LIMIT = getattr(settings, "OTP_MAX_REQUESTS", 4)


def can_send_otp(email):
    """
    Check if an OTP can be sent to the given email.
    - Limits requests to a configurable max (default: 4) in a rolling 24-hour window.
    - Prevents OTP spam (1 per minute).
    """
    time_threshold = timezone.now() - timedelta(hours=24)
    last_minute_threshold = timezone.now() - timedelta(
        minutes=1)  # New cooldown check

    request_count = OTPRequest.objects.filter(
        email=email, created_at__gte=time_threshold).count()
    last_request = OTPRequest.objects.filter(
        email=email, created_at__gte=last_minute_threshold).exists()

    remaining_attempts = OTP_LIMIT - request_count

    if last_request:
        return False, "Please wait 1 minute before requesting another OTP."

    if request_count >= OTP_LIMIT:
        return False, f"You have reached the OTP limit ({OTP_LIMIT} per 24 hours). Try again later."

    return True, f"OTP can be sent. Remaining attempts: {remaining_attempts}"


def generate_otp():
    """Generate a secure 6-digit OTP."""
    return ''.join(random.choices(string.digits, k=6))


def send_otp_email(email, otp):
    """
    Sends OTP to the provided email.
    Returns True if sent successfully, otherwise False.
    """
    try:
        validate_email(email)
        subject = "Your OTP Code"
        message = f"Your OTP code is {otp}. It is valid for 5 minutes."

        if send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                     [email]) == 0:
            logger.error(f"Failed to send OTP to {email}.")
            return False

        logger.info(f"OTP sent successfully to {email}.")
        return True

    except (ValidationError, Exception) as e:
        logger.error(f"Error sending OTP to {email}: {e}")

    return False


def create_otp_request(user, email):
    """
    Generates OTP, stores it in DB securely (hashed), and sends it via email.
    Returns the generated OTP.
    """
    otp = generate_otp()
    hashed_otp = make_password(otp)  # Hash OTP before storing

    otp_request = OTPRequest.objects.create(user=user,
                                            email=email,
                                            otp=hashed_otp,
                                            expiration_time=timezone.now() +
                                            timedelta(minutes=5))

    if send_otp_email(email, otp):
        logger.info(f"OTP request created for {email} (user_id={user.id})")
        return otp

    logger.error(f"Failed to send OTP for {email}, deleting request.")
    otp_request.delete()  # Remove OTP if email sending fails
    return None


def validate_otp(email, otp_input):
    """
    Validates OTP within a 5-minute window.
    """
    try:
        otp_request = OTPRequest.objects.filter(
            email=email, expiration_time__gte=timezone.now()).order_by(
                '-expiration_time').first()

        if not otp_request:
            logger.warning(f"No valid OTP request found for {email}.")
            return False, "OTP expired or not found."

        if check_password(otp_input, otp_request.otp):  # Securely compare OTPs
            logger.info(f"OTP successfully verified for {email}.")
            return True, "OTP verified successfully."

        logger.warning(f"Invalid OTP entered for {email}.")
        return False, "Invalid OTP."

    except Exception as e:
        logger.error(f"Error validating OTP for {email}: {e}")
        return False, "Error occurred during OTP validation."
