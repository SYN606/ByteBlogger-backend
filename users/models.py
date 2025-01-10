from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta


def get_expiration_time():
    return timezone.now() + timedelta(minutes=5)


class User(AbstractUser):
    is_verified = models.BooleanField(default=False)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='profile')
    avatar = models.ImageField(upload_to='profile_avatars/',
                               null=True,
                               blank=True)
    full_name = models.CharField(max_length=255)
    topic_interests = models.TextField()

    def __str__(self):
        return self.full_name


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
