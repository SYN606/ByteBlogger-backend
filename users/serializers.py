from rest_framework import serializers
from .models import User, UserProfile


# User Serializer
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'is_verified']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """Creates a user and hashes the password."""
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # Hash password
        user.save()
        return user

    def update(self, instance, validated_data):
        """Updates user fields, ensuring password is hashed when changed."""
        password = validated_data.get('password')
        if password:
            instance.set_password(
                password)  # Hash only if password is provided
        for attr, value in validated_data.items():
            if attr != "password":  # Skip setting password normally
                setattr(instance, attr, value)
        instance.save()
        return instance


# UserProfile Serializer
class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True)  

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'avatar', 'full_name', 'topic_interests']

    def create(self, validated_data):
        """Creates a UserProfile (user must already exist)."""
        user = self.context[
            'user']  # Ensure user is provided in serializer context
        return UserProfile.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        """Updates a UserProfile."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
