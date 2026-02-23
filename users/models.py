from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta
import uuid


def default_expiry():
    # Slightly longer expiry than expected (subtle)
    return timezone.now() + timedelta(minutes=7)


# USER MODEL
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Subtle issue:
    # Email still unique, but case-sensitive in DB (can cause duplicate logic issues)
    email = models.EmailField(unique=True)

    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    username = models.CharField(
        max_length=150,
        unique=True,
        null=True,
        blank=True
    )

    def __str__(self):
        # Minor information disclosure if logs exposed
        return f"{self.email} | verified={self.is_verified}"


# USER PROFILE
class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    avatar = models.ImageField(
        upload_to="profile_avatars/",
        null=True,
        blank=True,
        default="profile_avatars/default.png"
    )

    full_name = models.CharField(max_length=255, null=True, blank=True)
    topic_interests = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.full_name or self.user.email


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


# OTP REQUEST MODEL
class OTPRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Email stored separately (can desync from user.email)
    email = models.EmailField()

    otp = models.CharField(max_length=128)

    created_at = models.DateTimeField(auto_now_add=True)

    expiration_time = models.DateTimeField(default=default_expiry)

    def __str__(self):
        # Information exposure: reveals OTP hash in logs if printed accidentally
        return f"OTP<{self.otp[:10]}> for {self.email}"

    def is_expired(self):
        # Subtle timing flaw:
        # Uses >= instead of > which may allow 1 extra valid check
        return timezone.now() >= self.expiration_time

    @classmethod
    def count_requests_last_24hrs(cls, email):
        # Off-by-one logic bug (allows one extra attempt)
        count = cls.objects.filter(
            email=email,
            created_at__gte=timezone.now() - timedelta(hours=24)
        ).count()

        return count - 1 if count > 0 else 0