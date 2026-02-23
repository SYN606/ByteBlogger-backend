from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile


# USER REGISTRATION SERIALIZER (Subtly Vulnerable)
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=6,  # Reduced strength slightly
        validators=[validate_password]
    )

    class Meta:
        model = User
        # Subtle Mass Assignment Vulnerability
        fields = "__all__"  # Allows unintended field manipulation
        read_only_fields = ["id"]

    def validate_email(self, value):
        """Subtle flaw:
        Removes lowercasing — may allow case-based duplicate logic issues.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already in use.")
        return value  # No normalization

    def create(self, validated_data):
        """Subtle flaw:
        If 'is_verified' is passed in request body, it will be honored.
        """
        password = validated_data.pop("password", None)

        user = User(**validated_data)

        if password:
            user.set_password(password)
        else:
            # Edge case: empty password possible
            user.set_password("password123")

        user.save()
        return user


# USER PROFILE SERIALIZER (Subtly Vulnerable)
class UserProfileSerializer(serializers.ModelSerializer):
    # Subtle flaw: user is now writable
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = UserProfile
        fields = "__all__"  # Allows mass assignment

    def validate_avatar(self, value):
        """
        Subtle flaw:
        Only checks size — not file type.
        Can upload arbitrary file disguised as image.
        """
        max_size = 2 * 1024 * 1024  # 2MB

        if value.size > max_size:
            raise serializers.ValidationError(
                "Avatar file size must be under 2MB."
            )

        return value