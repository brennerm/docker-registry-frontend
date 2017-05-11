import tempfile
from unittest import TestCase

from docker_registry_frontend.storage import DockerRegistryJsonFileStorage, DockerRegistrySQLiteStorage
from docker_registry_frontend.registry import DockerV2Registry


class TestDockerRegistryStorage:
    def test_add_registry(self):
        self.storage.add_registry('localhost', 'http://localhost:80')
        self.assertEqual(
            self.storage.get_registries(),
            {
                '1': DockerV2Registry('localhost', 'http://localhost:80')
            }
        )

    def test_remove_registry(self):
        self.storage.add_registry('localhost', 'http://localhost:80')
        self.assertEqual(len(self.storage.get_registries()), 1)

        self.storage.remove_registry(
            '1'
        )
        self.assertEqual(len(self.storage.get_registries()), 0)

    def test_get_registries(self):
        self.assertEqual(self.storage.get_registries(), {})

        self.storage.add_registry('localhost', 'http://localhost:80')
        self.assertEqual(
            self.storage.get_registries(),
            {
                '1': DockerV2Registry('localhost', 'http://localhost:80')
            }
        )


class TestDockerRegistryJsonFileStorage(TestCase, TestDockerRegistryStorage):
    def setUp(self):
        self.tempfile = tempfile.NamedTemporaryFile(mode='w')
        self.tempfile.write('{}')
        self.tempfile.flush()

        self.storage = DockerRegistryJsonFileStorage(self.tempfile.name)

    def tearDown(self):
        self.tempfile.close()


class TestDockerRegistrySQLiteStorage(TestCase, TestDockerRegistryStorage):
    def setUp(self):
        self.tempfile = tempfile.NamedTemporaryFile(mode='w')
        self.storage = DockerRegistrySQLiteStorage(self.tempfile.name)

    def tearDown(self):
        self.tempfile.close()
