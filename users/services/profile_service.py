# accounts/services/profile_service.py

from django.shortcuts import get_object_or_404
from django.db import transaction

from ..models import UserProfile


def get_user_profile(user, serializer_class):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    serializer = serializer_class(profile)
    return True, serializer.data, 200


@transaction.atomic
def update_profile_or_password(user, data, serializer_class):
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    # Handle password change
    if old_password and new_password:
        if not user.check_password(old_password):
            return False, {"error": "Old password is incorrect."}, 400

        user.set_password(new_password)
        user.save()

        return True, {"message": "Password updated successfully."}, 200

    # Handle profile update
    profile = get_object_or_404(UserProfile, user=user)

    serializer = serializer_class(profile, data=data, partial=True)

    if not serializer.is_valid():
        return False, serializer.errors, 400

    serializer.save()

    return True, {"message": "Profile updated successfully."}, 200
