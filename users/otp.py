import random
import string
import logging
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from .models import OTPRequest

logger = logging.getLogger(__name__)


def can_send_otp(email):
    """
    Check if an OTP can be sent. Limits to 4 requests per 24 hours.
    """
    otp_count = OTPRequest.count_requests_in_last_24hrs(email)
    if otp_count >= 4:
        logger.warning(f"OTP request limit reached for {email}.")
        return False, "You can only request 4 OTPs within 24 hours."
    return True, "OTP can be sent."


# Generate a secure OTP (6 digits)
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))


# Send OTP to the user's email
def send_otp_email(email, otp):
    try:
        subject = 'Your OTP Code'
        message = f'Your OTP code is {otp}. It is valid for 5 minutes.'
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
        logger.info(f"OTP sent to {email}")
    except Exception as e:
        logger.error(f"Failed to send OTP to {email}: {str(e)}")


# Create OTP request and store it in the database
def create_otp_request(user, email):
    otp = generate_otp()

    # Create OTP request in the database
    otp_request = OTPRequest.objects.create(
        user=user,
        email=email,
        otp=otp,
        expiration_time=timezone.now() +
        timedelta(minutes=5)  # OTP is valid for 5 minutes
    )

    # Send OTP to email
    send_otp_email(email, otp)
    logger.info(f"OTP request created for {email} (user_id={user.id})")

    return otp_request.otp  # Returning OTP directly, as it's the main outcome


# Validate OTP from the database
def validate_otp(email, otp_input):
    try:
        # Retrieve the latest OTP request for the email
        otp_request = OTPRequest.objects.filter(
            email=email,
            request_time__gte=timezone.now() - timedelta(
                minutes=5)  # Only consider OTPs within the last 5 minutes
        ).order_by('-request_time').first()

        if not otp_request:
            logger.warning(f"No recent OTP request found for {email}.")
            return False, "OTP not found or expired."

        if otp_request.is_valid(otp_input):
            logger.info(f"OTP verified for {email}.")
            return True, "OTP verified successfully."

        logger.warning(f"Invalid OTP entered for {email}.")
        return False, "Invalid OTP."

    except Exception as e:
        logger.error(f"Error validating OTP for {email}: {str(e)}")
        return False, "An error occurred while validating OTP."
