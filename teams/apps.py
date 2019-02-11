from django.apps import AppConfig


class TeamsConfig(AppConfig):
    name = 'teams'
    verbose_name = "Teams"

    def ready(self):
        import teams.signals # noqa
