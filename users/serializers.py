from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile


# USER SERIALIZER 
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,
                                     required=True,
                                     validators=[validate_password],
                                     min_length=8)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password']
        read_only_fields = ['id']

    def validate_email(self, value):
        """
        Normalize and enforce case-insensitive uniqueness.
        """
        email = value.lower()

        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("Email already in use.")

        return email

    def validate_username(self, value):
        if value and User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username already taken.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')

        user = User(**validated_data)
        user.set_password(password)
        user.is_verified = False  # Ensure user cannot self-verify
        user.save()

        return user

    def update(self, instance, validated_data):
        """
        Restrict updates to safe fields only.
        Password changes should be handled separately.
        """
        validated_data.pop("password", None)
        validated_data.pop("is_verified", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


# USER PROFILE SERIALIZER 
class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    avatar = serializers.ImageField(
        required=False,
        allow_null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "webp"])
        ])

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'avatar', 'full_name', 'topic_interests']
        read_only_fields = ['id', 'user']

    def validate_avatar(self, value):
        """
        Validate file size and ensure safe upload.
        """
        max_size = 2 * 1024 * 1024  # 2MB

        if value.size > max_size:
            raise serializers.ValidationError(
                _("Avatar file size must be under 2MB."))

        return value

    def update(self, instance, validated_data):
        """
        Only update allowed profile fields.
        """
        allowed_fields = ["avatar", "full_name", "topic_interests"]

        for attr in allowed_fields:
            if attr in validated_data:
                setattr(instance, attr, validated_data[attr])

        instance.save()
        return instance
