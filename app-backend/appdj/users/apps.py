from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'appdj.users'
    verbose_name = "Users"

    def ready(self):
        from . import signals # noqa
