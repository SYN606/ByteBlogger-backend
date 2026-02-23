from django.shortcuts import get_object_or_404
from django.db import transaction

from users.models import UserProfile


def get_profile(user, serializer_class):
    profile = get_object_or_404(UserProfile, user=user)
    serializer = serializer_class(profile)
    return True, serializer.data, 200


@transaction.atomic
def update_profile(user, data, serializer_class):
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    if old_password and new_password:
        if not user.check_password(old_password):
            return False, {"error": "Old password incorrect."}, 400

        user.set_password(new_password)
        user.save(update_fields=["password"])
        return True, {"message": "Password updated."}, 200

    profile = get_object_or_404(UserProfile, user=user)

    serializer = serializer_class(profile, data=data, partial=True)
    if not serializer.is_valid():
        return False, serializer.errors, 400

    serializer.save()
    return True, {"message": "Profile updated."}, 200
