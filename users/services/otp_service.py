from django.shortcuts import get_object_or_404
from django.db import transaction

from users.models import User
from users.utils.otp import validate_otp, create_otp_request


@transaction.atomic
def verify_otp(user_id, otp_input):
    user = get_object_or_404(User, id=user_id)

    success, message = validate_otp(user, otp_input)

    if not success:
        return False, {"error": message}, 400

    user.is_verified = True
    user.save(update_fields=["is_verified"])

    return True, {"message": "User verified successfully."}, 200


def resend_otp(user_id):
    user = get_object_or_404(User, id=user_id)

    if user.is_verified:
        return False, {"error": "User already verified."}, 400

    success, message = create_otp_request(user)

    if not success:
        return False, {"error": message}, 400

    return True, {"message": "OTP resent successfully."}, 200