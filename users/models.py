from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import EmailValidator
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from datetime import timedelta
import uuid

OTP_EXPIRY_MINUTES = 5


def default_expiry():
    return timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)


# USER MODEL 
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        db_index=True,
    )

    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    username = models.CharField(max_length=150,
                                unique=True,
                                null=True,
                                blank=True)

    class Meta:
        constraints = [
            # Case-insensitive unique email
            UniqueConstraint(Lower("email"), name="unique_lower_email")
        ]

    def save(self, *args, **kwargs):
        # Normalize email before saving
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


# USER PROFILE
class UserProfile(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name="profile")

    avatar = models.ImageField(upload_to="profile_avatars/",
                               null=True,
                               blank=True,
                               default="profile_avatars/default.png")

    full_name = models.CharField(max_length=255, null=True, blank=True)
    topic_interests = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.full_name or self.user.email


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


# OTP REQUEST (HARDENED)
class OTPRequest(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name="otp_requests")

    # Store hashed OTP only
    otp_hash = models.CharField(max_length=128)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    expiration_time = models.DateTimeField(default=default_expiry,
                                           db_index=True)

    is_used = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["expiration_time"]),
        ]

    def is_expired(self):
        return timezone.now() > self.expiration_time

    def mark_used(self):
        self.is_used = True
        self.save(update_fields=["is_used"])

    @classmethod
    def active_otp_for_user(cls, user):
        """
        Returns latest unused, non-expired OTP.
        """
        return cls.objects.filter(
            user=user, is_used=False,
            expiration_time__gte=timezone.now()).order_by(
                "-created_at").first()

    @classmethod
    def count_requests_last_24hrs(cls, user):
        return cls.objects.filter(user=user,
                                  created_at__gte=timezone.now() -
                                  timedelta(hours=24)).count()

    def __str__(self):
        return f"OTP request for {self.user.email}"
