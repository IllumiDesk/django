import factory
from uuid import uuid4
from factory import fuzzy
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model

from appdj.base.tests.factories import FuzzyEmail
from ..models import UserProfile, Email
# from ..signals import create_user_ssh_key

User = get_user_model()


class UserProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProfile


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username', 'email')

    @factory.sequence
    def username(n):
        return f"user_{str(uuid4())[:16]}"

    email = FuzzyEmail()
    password = factory.PostGenerationMethodCall('set_password', 'default')

    @classmethod
    def _generate(cls, create, attrs):
        # post_save.disconnect(create_user_ssh_key, User)
        user = super()._generate(create, attrs)
        user.is_staff = True
        user.save()
        # post_save.connect(create_user_ssh_key, User)
        return user


class EmailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Email
    user = factory.SubFactory(UserFactory)
    address = FuzzyEmail()
    public = fuzzy.FuzzyChoice([True, False])
    unsubscribed = fuzzy.FuzzyChoice([True, False])
