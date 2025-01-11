from rest_framework import serializers
from .models import User, UserProfile, NewsletterSubscription


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
    user = UserSerializer()  # Nested User Serializer
    newsletter_subscription = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'avatar', 'full_name', 'topic_interests',
            'newsletter_subscription'
        ]

    def get_newsletter_subscription(self, obj):
        # Fetch the latest subscription if available
        subscription = obj.user.newsletter_subscriptions.first()
        if subscription:
            return {
                'email': subscription.email,
                'subscribed_on': subscription.subscribed_on
            }
        return None

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserSerializer.create(UserSerializer(),
                                     validated_data=user_data)
        user_profile = UserProfile.objects.create(user=user, **validated_data)

        # Handle newsletter subscription
        if validated_data.get('newsletter', False):
            NewsletterSubscription.objects.create(user=user, email=user.email)

        return user_profile

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            UserSerializer.update(UserSerializer(),
                                  instance=instance.user,
                                  validated_data=user_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Handle newsletter subscription
        newsletter_flag = validated_data.get('newsletter')
        if newsletter_flag is not None:
            if newsletter_flag:
                # Subscribe to the newsletter
                if not NewsletterSubscription.objects.filter(
                        user=instance.user).exists():
                    NewsletterSubscription.objects.create(
                        user=instance.user, email=instance.user.email)
            else:
                # Unsubscribe from the newsletter
                NewsletterSubscription.objects.filter(
                    user=instance.user).delete()

        instance.save()
        return instance


# Newsletter Subscription Serializer
class NewsletterSubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = NewsletterSubscription
        fields = ['email', 'subscribed_on', 'user']
