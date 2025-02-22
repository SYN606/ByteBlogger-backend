from rest_framework import serializers
from .models import User, UserProfile


# User Serializer
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'is_verified']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


# UserProfile Serializer
class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()  

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'avatar', 'full_name', 'topic_interests',
        ]


    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserSerializer.create(UserSerializer(), 
                                     validated_data=user_data)
        user_profile = UserProfile.objects.create(user=user, **validated_data)


        return user_profile

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            UserSerializer.update(UserSerializer(),
                                  instance=instance.user,
                                  validated_data=user_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)



        instance.save()
        return instance


