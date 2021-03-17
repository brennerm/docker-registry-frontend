import abc
import json
import os
import sqlite3

from docker_registry_frontend.registry import make_registry


class DockerRegistryWebStorage(abc.ABC):
    def get_registries(self):
        raise NotImplementedError

    def add_registry(self, name, url, user=None, password=None):
        raise NotImplementedError

    def update_registry(self, identifier, name, url, user=None, password=None):
        raise NotImplementedError

    def empty(self):
        raise NotImplementedError

    def remove_registry(self, identifier):
        raise NotImplementedError


class DockerRegistryEnvStorage(DockerRegistryWebStorage):
    def get_registries(self):
        return {
            "1": make_registry(
                name=os.environ["DOCKER_REGISTRY_FRONTEND_NAME"],
                url=os.environ["DOCKER_REGISTRY_FRONTEND_URL"],
                user=os.environ["DOCKER_REGISTRY_FRONTEND_USER"],
                password=os.environ["DOCKER_REGISTRY_FRONTEND_PASSWORD"]
            )
        }

    def update_registry(self, identifier, name, url, user=None, password=None):
        pass

    def empty(self):
        pass

    def remove_registry(self, identifier):
        pass

    def add_registry(self, name, url, user=None, password=None):
        pass


STORAGE_DRIVERS = {
    'env': DockerRegistryEnvStorage
}
