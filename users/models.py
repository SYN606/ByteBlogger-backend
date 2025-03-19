from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid


def get_expiration_time():
    return timezone.now() + timedelta(minutes=5)


# User model
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_verified = models.BooleanField(default=False)
    email = models.EmailField(unique=True)

    # Use email for login instead of username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Username is now optional

    username = models.CharField(max_length=150,
                                unique=True,
                                null=True,
                                blank=True)  # Optional username

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='profile')

    avatar = models.ImageField(
        upload_to='profile_avatars/',
        null=True,
        blank=True,
        default='profile_avatars/default.png'  # Set default image
    )
    full_name = models.CharField(max_length=255, null=True,
                                 blank=True)  # Optional full name
    topic_interests = models.TextField(null=True,
                                       blank=True)  # Optional interests

    def __str__(self):
        return self.full_name if self.full_name else self.user.email


# Signal to create UserProfile when a User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


# OTPRequest model
class OTPRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    request_time = models.DateTimeField(default=timezone.now)
    expiration_time = models.DateTimeField(default=get_expiration_time)

    def __str__(self):
        return f"OTP request for {self.user.email} at {self.request_time}"

    def is_expired(self):
        return timezone.now() > self.expiration_time

    def is_valid(self, otp_input):
        return self.otp == otp_input and not self.is_expired()

    @classmethod
    def count_requests_in_last_24hrs(cls, email):
        return cls.objects.filter(user__email=email,
                                  request_time__gte=timezone.now() -
                                  timedelta(hours=24)).count()
