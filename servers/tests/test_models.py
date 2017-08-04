from uuid import UUID

from django.test import TestCase
from django_redis import get_redis_connection

from projects.tests.factories import CollaboratorFactory
from servers.models import Server
from servers.tests.factories import ServerFactory


class TestServer(TestCase):
    def setUp(self):
        self.cache = get_redis_connection("default")
        self.pk = UUID('{00000000-0000-0000-0000-000000000000}')

    def tearDown(self):
        self.cache.flushall()

    def test_str(self):
        instance = Server(id=self.pk, name='test')
        self.assertEqual(str(instance), instance.name)

    def test_container_name(self):
        expected = "server_00000000-0000-0000-0000-000000000000_test"
        server = Server(name="test", id=self.pk)
        self.assertEqual(server.container_name, expected)

    def test_volume_path(self):
        collaborator = CollaboratorFactory(user__username='test', project__id=self.pk)
        server = Server(project=collaborator.project)
        expected = '/tmp/test/00000000-0000-0000-0000-000000000000'
        self.assertEqual(server.volume_path, expected)

    def test_state_cache_key(self):
        server = Server(id=self.pk)
        expected = 'server_state_00000000-0000-0000-0000-000000000000'
        self.assertEqual(server.state_cache_key, expected)

    def test_needs_update(self):
        server = Server(id=self.pk)
        self.cache.hset('server_state_00000000-0000-0000-0000-000000000000', 'update', 'test')
        self.assertTrue(server.needs_update())

    def test_update_message(self):
        server = Server(id=self.pk)
        msg = 'test'
        self.cache.hset('server_state_00000000-0000-0000-0000-000000000000', 'update', msg)
        self.assertEqual(server.update_message, msg)

    def test_update_message_setter(self):
        server = Server(id=self.pk)
        msg = 'test'
        server.update_message = msg
        self.assertEqual(self.cache.hget('server_state_00000000-0000-0000-0000-000000000000', "update").decode(), msg)

    def test_update_message_deleter(self):
        server = Server(id=self.pk)
        msg = 'test'
        self.cache.hset('server_state_00000000-0000-0000-0000-000000000000', 'update', msg)
        del server.update_message
        self.assertFalse(bool(self.cache.hexists('server_state_00000000-0000-0000-0000-000000000000', "update")))

    def test_server_container_name_has_no_spaces(self):
        server = ServerFactory(name=" I have spaces ")
        self.assertFalse(" " in server.container_name)
