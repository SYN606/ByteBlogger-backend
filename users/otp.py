import random
import string
import logging
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from .models import OTPRequest
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import smtplib

logger = logging.getLogger(__name__)


def can_send_otp(email):
    """
    Check if an OTP can be sent (Max 4 OTPs in 24 hours).
    """
    if OTPRequest.count_requests_in_last_24hrs(email) >= 4:
        logger.warning(f"OTP limit reached for {email}.")
        return False, "You can request up to 4 OTPs per 24 hours."
    return True, "OTP can be sent."


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

    except (ValidationError, smtplib.SMTPRecipientsRefused) as e:
        logger.error(
            f"Invalid email or recipient refused: {email}. Error: {e}")
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error occurred for {email}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error while sending OTP to {email}: {e}")

    return False


def create_otp_request(user, email):
    """
    Generates OTP, stores it in DB, and sends it via email.
    Returns the generated OTP.
    """
    otp = generate_otp()

    otp_request = OTPRequest.objects.create(user=user,
                                            email=email,
                                            otp=otp,
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
            email=email,
            request_time__gte=timezone.now() -
            timedelta(minutes=5)).order_by('-request_time').first()

        if not otp_request:
            logger.warning(f"No valid OTP request found for {email}.")
            return False, "OTP expired or not found."

        if otp_request.is_valid(otp_input):
            logger.info(f"OTP successfully verified for {email}.")
            return True, "OTP verified successfully."

        logger.warning(f"Invalid OTP entered for {email}.")
        return False, "Invalid OTP."

    except Exception as e:
        logger.error(f"Error validating OTP for {email}: {e}")
        return False, "Error occurred during OTP validation."
