from django.db import models
from django.contrib.auth.models import AbstractUser


# Custom User model
class User(AbstractUser):
    is_verified = models.BooleanField(default=False)
    email = models.EmailField(
        unique=True)  # Email is unique and used for login
    password = models.CharField(max_length=255)

    # Make email the username field for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username'
    ]  # 'username' is required for user creation but not for login

    def __str__(self):
        return self.email


# UserProfile model
class UserProfile(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='profile')
    avatar = models.ImageField(upload_to='profile_avatars/',
                               null=True,
                               blank=True)
    full_name = models.CharField(max_length=255)
    email_address = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True)
    topic_interests = models.TextField()

    def __str__(self):
        return self.full_name
