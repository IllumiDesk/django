from celery import shared_task
from .spawners import SwarmModeSpawner
from .models import Server


def server_action(action: str, server_pk: str):
    server = Server.objects.get(pk=server_pk)
    spawner = SwarmModeSpawner(server)
    getattr(spawner, action)()


@shared_task()
def start_server(server_pk):
    server_action('start', server_pk)


@shared_task()
def stop_server(server_pk):
    server_action('stop', server_pk)


@shared_task()
def terminate_server(server_pk):
    server_action('terminate', server_pk)
    Server.objects.filter(pk=server_pk).delete()
