import secrets
import logging
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import (
    make_password,
    check_password,
)
from django.db import transaction

from users.models import OTPRequest

logger = logging.getLogger(__name__)

OTP_LIMIT = getattr(settings, "OTP_MAX_REQUESTS", 4)
OTP_EXPIRY_MINUTES = getattr(settings, "OTP_EXPIRY_MINUTES", 5)
OTP_COOLDOWN_SECONDS = 60


# RATE LIMITING
def can_send_otp(user):
    """
    Enforce strict per-user OTP limits.
    """

    now = timezone.now()

    last_24_hours = now - timedelta(hours=24)

    cooldown_window = now - timedelta(
        seconds=OTP_COOLDOWN_SECONDS,
    )

    request_count = OTPRequest.objects.filter(
        user=user,
        created_at__gte=last_24_hours,
    ).count()

    cooldown_active = OTPRequest.objects.filter(
        user=user,
        created_at__gte=cooldown_window,
    ).exists()

    if cooldown_active:
        return (
            False,
            "Please wait before requesting another OTP.",
        )

    if request_count >= OTP_LIMIT:
        return (
            False,
            "OTP request limit reached. Try again later.",
        )

    return True, None


# OTP GENERATION
def generate_otp():
    """
    Generate cryptographically secure 6-digit OTP.
    """

    return "".join(
        str(secrets.randbelow(10))
        for _ in range(6)
    )


# EMAIL SENDING
def send_otp_email(email, otp):
    """
    Send OTP email using Django SMTP backend.
    """

    try:
        validate_email(email)

        subject = "Your OTP Code"

        message = (
            f"Your OTP code is {otp}.\n\n"
            f"This code is valid for "
            f"{OTP_EXPIRY_MINUTES} minutes.\n\n"
            f"If you did not request this OTP, "
            f"please ignore this email."
        )

        sent = send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        if sent > 0:
            logger.info(
                "OTP email sent successfully to %s",
                email,
            )
            return True

        logger.warning(
            "OTP email was not sent to %s",
            email,
        )

        return False

    except ValidationError:
        logger.warning(
            "Invalid email address provided: %s",
            email,
        )
        return False

    except Exception:
        logger.exception(
            "Failed to send OTP email to %s",
            email,
        )
        return False


# CREATE OTP REQUEST
@transaction.atomic
def create_otp_request(user):
    """
    Creates a new OTP request for a user.

    Features:
    - Enforces cooldown + daily rate limit
    - Invalidates old OTPs
    - Stores hashed OTP only
    - Rolls back on email failure
    """

    allowed, message = can_send_otp(user)

    if not allowed:
        return False, message

    # Invalidate previous OTPs
    OTPRequest.objects.filter(
        user=user,
        is_used=False,
        expiration_time__gte=timezone.now(),
    ).update(
        is_used=True,
    )

    raw_otp = generate_otp()

    hashed_otp = make_password(raw_otp)

    otp_request = OTPRequest.objects.create(
        user=user,
        otp_hash=hashed_otp,
        expiration_time=timezone.now()
        + timedelta(
            minutes=OTP_EXPIRY_MINUTES,
        ),
    )

    if send_otp_email(
        user.email,
        raw_otp,
    ):
        return (
            True,
            "OTP sent successfully.",
        )

    # Rollback if email fails
    otp_request.delete()

    return (
        False,
        "Failed to send OTP.",
    )


# VALIDATE OTP
@transaction.atomic
def validate_otp(user, otp_input):
    """
    Validate OTP securely.

    Features:
    - Constant-time hash comparison
    - Expiration enforcement
    - Replay protection
    """

    otp_request = OTPRequest.active_otp_for_user(
        user,
    )

    if not otp_request:
        return (
            False,
            "Invalid or expired OTP.",
        )

    if otp_request.is_expired():

        otp_request.is_used = True

        otp_request.save(
            update_fields=["is_used"],
        )

        return (
            False,
            "Invalid or expired OTP.",
        )

    if not check_password(
        otp_input,
        otp_request.otp_hash,
    ):
        return (
            False,
            "Invalid or expired OTP.",
        )

    # Prevent replay attacks
    otp_request.mark_used()

    return (
        True,
        "OTP verified successfully.",
    )