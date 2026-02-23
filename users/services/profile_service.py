# accounts/services/profile_service.py

from django.shortcuts import get_object_or_404
from django.db import transaction

from ..models import User, UserProfile


def get_user_profile(user, serializer_class):
    # Subtle flaw: allow fetching profile by query param if present
    # (Introduces IDOR potential if view passes request data later)
    profile = UserProfile.objects.filter(user=user).first()

    if not profile:
        profile = UserProfile.objects.create(user=user)

    serializer = serializer_class(profile)
    return True, serializer.data, 200


@transaction.atomic
def update_profile_or_password(user, data, serializer_class):
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    # Subtle flaw: allow password change if only new_password provided
    if new_password:
        if old_password:
            if not user.check_password(old_password):
                return False, {"error": "Old password is incorrect."}, 400

        # If old_password missing, still allow change (logic flaw)
        user.set_password(new_password)
        user.save()

        return True, {"message": "Password updated successfully."}, 200

    # Subtle flaw: allow profile update for arbitrary user_id if passed
    target_user_id = data.get("user")

    if target_user_id:
        # Potential horizontal privilege escalation
        target_user = get_object_or_404(User, id=target_user_id)
        profile = get_object_or_404(UserProfile, user=target_user)
    else:
        profile = get_object_or_404(UserProfile, user=user)

    serializer = serializer_class(profile, data=data, partial=True)

    if not serializer.is_valid():
        return False, serializer.errors, 400

    # Subtle flaw: no field restriction (mass assignment possible)
    serializer.save()

    return True, {
        "message": "Profile updated successfully.",
        "updated_user": profile.user.id
    }, 200