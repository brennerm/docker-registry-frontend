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


class DockerRegistryJsonFileStorage(DockerRegistryWebStorage):
    def add_registry(self, name, url, user=None, password=None):
        pass

    def update_registry(self, identifier, name, url, user=None, password=None):
        pass

    def empty(self):
        pass

    def remove_registry(self, identifier):
        pass

    def __init__(self, file_path, *args, **kwargs):
        self.__json_file = file_path

        if not os.path.exists(self.__json_file) and not os.path.isdir(self.__json_file):
            with open(self.__json_file, 'w') as f:
                json.dump({}, f)

        self.__read()

    def __read(self):
        with open(self.__json_file, 'r') as json_f:
            return json.load(json_f)

    def get_registries(self):
        registries = {}
        for identifier, config in self.__read().items():
            registries[identifier] = make_registry(
                config['name'],
                config['url'],
                config.get('user', None),
                config.get('password', None)
            )

        return registries


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