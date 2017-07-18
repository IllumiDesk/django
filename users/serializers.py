from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.authtoken.serializers import AuthTokenSerializer as RestAuthTokenSerializer
from social_django.models import UserSocialAuth

from base.views import RequestUserMixin
from base.serializers import SearchSerializerMixin
from users.models import UserProfile, Email
User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('avatar_url', 'bio', 'url', 'location', 'company', 'timezone')


class UserSerializer(SearchSerializerMixin, serializers.ModelSerializer):
    profile = UserProfileSerializer()

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

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        profile = UserProfile(user=user, **profile_data)
        profile.save()
        Email.objects.create(user=user, address=validated_data['email'])
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.get('profile')
        if profile_data is not None:
            validated_data.pop('profile')
            profile = UserProfile(user=instance, **profile_data)
            profile.save()
        password = validated_data.pop('password', None)
        if password is not None:
            instance.set_password(password)
        return super().update(instance, validated_data)


class EmailSerializer(RequestUserMixin, serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = ('id', 'address', 'public', 'unsubscribed')
        read_only_fields = ("id",)


class IntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSocialAuth
        fields = ('provider', 'extra_data')

    extra_data = serializers.JSONField(required=False)


class AuthTokenSerializer(RestAuthTokenSerializer):
    username = serializers.CharField(label="Username", write_only=True)
    password = serializers.CharField(label="Password", style={'input_type': 'password'}, write_only=True)
    token = serializers.CharField(label="Token", read_only=True)
