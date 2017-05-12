import abc
import functools
import json
import operator


class DockerRegistryManifest(abc.ABC):
    def __init__(self, content):
        self._content = content

    def get_number_of_layers(self):
        raise NotImplementedError

    def get_created_date(self):
        raise NotImplementedError

    def get_entrypoint(self):
        raise NotImplementedError

    def get_exposed_ports(self):
        raise NotImplementedError

    def get_docker_version(self):
        raise NotImplementedError

    def get_volumes(self):
        raise NotImplementedError


class DockerRegistrySchema1Manifest(DockerRegistryManifest):
    def __get_sorted_history(self):
        history = []

        for entry in self._content['history']:
            history.append(json.loads(entry['v1Compatibility']))

        history.sort(key=lambda x: x['created'], reverse=True)
        return history

    def __get_first_value(self, *keys):
        for entry in self.__get_sorted_history():
            try:
                return functools.reduce(operator.getitem, keys, entry)
            except KeyError:
                pass
        return None

    def get_created_date(self):
        return self.__get_first_value('created')

    def get_docker_version(self):
        return self.__get_first_value('docker_version')

    def get_entrypoint(self):
        return self.__get_first_value('config', 'Entrypoint')

    def get_exposed_ports(self):
        return self.__get_first_value('config', 'ExposedPorts')

    def get_layer_ids(self):
        layer_ids = []

        for layer in self._content['fsLayers']:
            layer_ids.append(layer['blobSum'])

        return layer_ids

    def get_number_of_layers(self):
        return len(self._content['fsLayers'])

    def get_volumes(self):
        return self.__get_first_value('config', 'Volumes')


def makeManifest(content):
    if content['schemaVersion'] == 1:
        return DockerRegistrySchema1Manifest(content)
    else:
        raise ValueError
