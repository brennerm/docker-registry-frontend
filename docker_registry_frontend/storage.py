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
    def __init__(self, file_path, *args, **kwargs):
        self.__json_file = file_path

        if not os.path.exists(self.__json_file) and not os.path.isdir(self.__json_file):
            with open(self.__json_file, 'w') as f:
                json.dump({}, f)

        self.__read()  # read for the first time to make sure given file is readable and contains valid JSON

    def __read(self):
        with open(self.__json_file, 'r') as json_f:
            return json.load(json_f)

    def __write(self, content):
        with open(self.__json_file, 'w') as json_f:
            json.dump(content, json_f)

    def __get_new_id(self):
        existing_ids = self.__read().keys()

        return str(max(
            [int(identifier) for identifier in existing_ids],
            default=0
        ) + 1)

    def add_registry(self, name, url, user=None, password=None):
        registries = self.__read()

        registries[self.__get_new_id()] = {
            'name': name,
            'url': url,
            'user': user,
            'password': password
        }

        self.__write(registries)

    def update_registry(self, identifier, name, url, user=None, password=None):
        registries = self.__read()

        if identifier not in registries:
            raise KeyError

        registries[identifier] = {
            'name': name,
            'url': url,
            'user': user,
            'password': password
        }

        self.__write(registries)

    def remove_registry(self, identifier):
        registries = self.__read()
        if identifier in registries:
            registries.pop(identifier)

        self.__write(registries)

    def empty(self):
        self.__write({})

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


class DockerRegistrySQLiteStorage(DockerRegistryWebStorage):
    def __init__(self, file_path, *args, **kwargs):
        self.__sqlite_file = file_path
        self.__conn = sqlite3.connect(file_path, check_same_thread=False)

        cursor = self.__conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS registries (id INTEGER PRIMARY KEY, name TEXT NOT NULL, url TEXT NOT NULL, user TEXT, password TEXT);")

    def __execute(self, *args, **kwargs):
        cursor = self.__conn.cursor()
        res = cursor.execute(*args, **kwargs)

        self.__conn.commit()
        return res

    def add_registry(self, name, url, user=None, password=None):
        self.__execute(
            f'INSERT INTO registries (name, url, user, password) VALUES (:name, :url, :user, :password);',
            {'name': name, 'url': url, 'user': user, 'password': password})

    def update_registry(self, identifier, name, url, user=None, password=None):
        self.__execute(
            'UPDATE registries SET name = :name, url = :url, user = :user, password = :password WHERE id = :id;',
            {'id': identifier, 'name': name, 'url': url, 'user': user,
             'password': password})

    def empty(self):
        self.__execute('DELETE FROM registries;')

    def remove_registry(self, identifier):
        self.__execute('DELETE FROM registries WHERE id = :id;', {'id': identifier})

    def get_registries(self):
        registries = {}

        for row in self.__execute('SELECT * FROM registries;'):
            identifier, name, url, user, password = row
            registries[str(identifier)] = make_registry(
                name,
                url,
                user,
                password
            )

        return registries


class DockerRegistryEnvStorage(DockerRegistryWebStorage):
    def __init__(self, *args, **kwargs):
        pass

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
    'sqlite': DockerRegistrySQLiteStorage,
    'json': DockerRegistryJsonFileStorage,
    'env': DockerRegistryEnvStorage
}
