import os
from django.core.management import BaseCommand
from django.conf import settings
from django.contrib.sites.models import Site


class Command(BaseCommand):
    def handle(self, *args, **options):
        site = Site.objects.get(pk=settings.SITE_ID)
        host = os.environ.get('TBS_HOST')
        port = os.environ.get('TBS_PORT')
        if port != '80':
            host = f'{host}:{port}'
        if host and site.domain == 'example.com':
            site.domain = host
            site.name = host
            site.save()
