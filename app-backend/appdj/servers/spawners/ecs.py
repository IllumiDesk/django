import os
import boto3
import logging
from typing import List, Dict, Tuple
from django.conf import settings
from django.utils.functional import cached_property

from .base import BaseSpawner

logger = logging.getLogger("servers")


class SpawnerException(Exception):
    pass


class ECSSpawner(BaseSpawner):
    def __init__(self, server, client=None) -> None:
        super().__init__(server)
        self.client = client or boto3.client('ecs')

    def start(self) -> None:
        logger.info(f"Starting server {self.server.pk}")
        if 'task_definition_arn' not in self.server.config:
            logger.info("Registering task definition")
            self.server.config['task_definition_arn'] = self._register_task_definition()
        resp = self.client.run_task(
            cluster=settings.ECS_CLUSTER,
            taskDefinition=self.server.config['task_definition_arn'],
        )
        self.server.config['task_arn'] = resp['tasks'][0]['taskArn']
        self.server.save()

    def stop(self) -> None:
        self.client.stop_task(
            cluster=settings.ECS_CLUSTER,
            task=self.server.config['task_arn'],
            reason='User request'
        )

    def terminate(self) -> None:
        self.stop()
        self.client.deregister_task_definition(
            taskDefinition=self.server.config['task_definition_arn']
        )

    def status(self) -> str:
        if 'task_arn' not in self.server.config:
            return self.server.STOPPED
        try:
            resp = self.client.describe_tasks(tasks=[self.server.config['task_arn']], cluster=settings.ECS_CLUSTER)
        except Exception as e:
            logger.exception("Error getting server status")
            return self.server.ERROR
        try:
            return resp['tasks'][0]['lastStatus'].title()
        except IndexError:
            logger.debug(resp)
            return self.server.ERROR

    def _register_task_definition(self) -> str:
        resp = self.client.register_task_definition(**self._task_definition_args)
        return resp['taskDefinition']['taskDefinitionArn']

    @cached_property
    def _task_definition_args(self):
        volumes, mount_points = self._get_volumes_and_mount_points()
        return dict(
            family='userspace',
            containerDefinitions=[
                {
                    'name': str(self.server.pk),
                    'image': self.server.image_name,
                    'cpu': self.server.server_size.cpu,
                    'memory': self.server.server_size.memory,
                    'memoryReservation': int(self.server.server_size.memory / 2),
                    'portMappings': self._get_port_mappings(),
                    'links': self._get_links(),
                    'essential': True,
                    'command': self._get_cmd(),
                    'environment': self._get_env(),
                    'linuxParameters': {
                        'devices': self._get_devices(),
                    },
                    'mountPoints': mount_points,
                    'dockerLabels': self._get_traefik_labels(),
                    'logConfiguration': {
                        'logDriver': 'awslogs',
                        'options': {
                            'awslogs-group': 'devUserspace',
                            'awslogs-region': settings.AWS_DEFAULT_REGION
                        }
                    },
                }
            ],
            volumes=volumes,
            placementConstraints=self._get_constrains()
        )

    def _get_links(self) -> List[str]:
        return [f'{name}:{alias}' for name, alias in super()._get_links().items()]

    def _get_constrains(self) -> List[str]:
        return []

    def _get_devices(self) -> List[Dict[str, str]]:
        dev_list = super()._get_devices()
        devices = []
        for dev in dev_list:
            host_path, container_path, _ = dev.split(":")
            devices.append({
                'hostPath': host_path,
                'containerPath': container_path
            })
        return devices

    def _get_env(self) -> List[Dict[str, str]]:
        return [{'name': k, 'value': v} for k, v in super()._get_env().items()]

    def _get_volumes_and_mount_points(self) -> Tuple[List[Dict[str, Dict[str, str]]], List[Dict[str, str]]]:
        logger.info("Getting volumes")
        volumes = [{'name': 'project', 'host': {'sourcePath': self.server.volume_path}}]
        mount_points = [{'sourceVolume': 'project', 'containerPath': settings.SERVER_RESOURCE_DIR}]
        if self.server.startup_script:
            volumes.append({
                'name': 'script',
                'host': {'sourcePath': os.path.join(self.server.volume_path, self.server.startup_script)}
            })
            mount_points.append({
                'sourceVolume': 'script',
                'containerPath': f'{settings.SERVER_RESOURCE_DIR}/start.sh'
            })
        return volumes, mount_points

    def _get_port_mappings(self) -> List[Dict[str, int]]:
        mappings = []
        for port in self._get_exposed_ports():
            mappings.append({
                'hostPort': 0,
                'containerPort': int(port)
            })
        return mappings

    def _get_traefik_labels(self) -> Dict[str, str]:
        labels = {"traefik.enable": "true"}
        server_uri = ''.join([
            f"/{settings.DEFAULT_VERSION}",
            f"/{self.server.project.owner.username}",
            f"/projects/{self.server.project_id}/servers",
            f"/{self.server.id}/endpoint/"
        ])
        for port in self._get_exposed_ports():
            endpoint = settings.SERVER_PORT_MAPPING.get(port)
            if endpoint:
                labels["traefik.port"] = port
                labels["traefik.frontend.rule"] = f"PathPrefix:{server_uri}{endpoint}"
        return labels