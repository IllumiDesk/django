import logging

from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import serializers
from social_django.models import UserSocialAuth

from appdj.base.views import RequestUserMixin
from appdj.base.serializers import SearchSerializerMixin
from .models import UserProfile, Email
from appdj.projects.models import Collaborator
from appdj.projects.utils import perform_project_copy

logger = logging.getLogger(__name__)
User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('bio', 'url', 'location', 'company', 'timezone', 'avatar', 'config')
        read_only_fields = ('avatar',)

    def to_representation(self, instance):
        initial_rep = super().to_representation(instance)
        request = self.context.get('request')
        if request and initial_rep['avatar'] is not None:
            avatar_url = request.build_absolute_uri(initial_rep['avatar'])
            if request.scheme == "http":
                avatar_url = avatar_url.replace("http", "https")
            initial_rep['avatar'] = avatar_url
        return initial_rep


class UserSerializer(SearchSerializerMixin, serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)
    email = serializers.EmailField(required=True, allow_blank=False, allow_null=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password', 'profile')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_username(self, value):
        user_exists = User.objects.filter(username=value,
                                          is_active=True).exists()
        if user_exists:
            raise serializers.ValidationError("{username} is already taken.".format(username=value))
        return value

    def validate_email(self, value):
        existing_user_email = User.objects.filter(email=value, is_active=True).exists()
        existing_secondary_email = Email.objects.filter(address=value,
                                                        user__is_active=True).exists()

        if existing_user_email or existing_secondary_email:
            logger.info(f"Rejected creating/updating user due to email conflict: {value}")
            raise serializers.ValidationError(f"The email {value} is taken")

        return value

    def create(self, validated_data):
        profile_data = {}
        if "profile" in validated_data:
            profile_data = validated_data.pop('profile')
        password = validated_data.pop('password')
        user = User(**validated_data, is_active=False)
        user.set_password(password)
        user.save()
        profile = UserProfile(user=user, **profile_data)
        profile.save()
        Email.objects.create(user=user, address=validated_data['email'])

        return user

    def update(self, instance, validated_data):
        if "profile" in validated_data:
            logger.info("Profile information found in update request. Setting information accordingly.")
            profile_data = validated_data.pop('profile')
            user_profile = UserProfile.objects.get(user=instance)

            for field in profile_data:
                setattr(user_profile, field, profile_data[field])

            user_profile.save()

        password = validated_data.pop('password', None)
        if password is not None:
            instance.set_password(password)

        for field in validated_data:
            setattr(instance, field, validated_data[field])

        instance.save()

        return instance


class EmailSerializer(RequestUserMixin, serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = ('id', 'user', 'address', 'public', 'unsubscribed')
        read_only_fields = ('id', 'user')

    def validate_address(self, value):
        existing_user_email = User.objects.filter(email=value, is_active=True).exists()
        existing_secondary_email = Email.objects.filter(address=value,
                                                        user__is_active=True).exists()

        if existing_user_email or existing_secondary_email:
            logger.info(f'Rejected creating/updating Email object due to email conflict: {value}')
            raise serializers.ValidationError(f"The email {value} is taken")

        return value


class IntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSocialAuth
        fields = ('id', 'provider', 'extra_data')

    extra_data = serializers.JSONField(required=False)