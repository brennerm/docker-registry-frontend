import abc
import functools
import json
import operator


class DockerRegistryManifest(abc.ABC):
    def __init__(self, content):
        self._content = content

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self._dict_as_str() == other._dict_as_str()

    def __hash__(self):
        return self._dict_as_str().__hash__()

    def _dict_as_str(self):
        return json.dumps(self._content, sort_keys=True)

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

        return set(layer_ids)

    def get_volumes(self):
        return self.__get_first_value('config', 'Volumes')


class DockerRegistrySchema2Manifest:
    def __init__(self, content):
        self._content = content

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self._dict_as_str() == other._dict_as_str()

    def __hash__(self):
        return self._dict_as_str().__hash__()

    def _dict_as_str(self):
        return json.dumps(self._content, sort_keys=True)

    def get_layers_count(self):
        return len(self._content["layers"])

    def get_layer_ids(self):
        layer_ids = []

        for layer in self._content['layers']:
            layer_ids.append(layer['digest'])

        return set(layer_ids)

    def get_size(self):
        return sum([layer["size"] for layer in self._content["layers"]])


class DockerRegistryCombinedManifest():
    def __init__(self, v1manifest: DockerRegistrySchema1Manifest,
                 v2manifest: DockerRegistrySchema2Manifest):
        self._v1manifest = v1manifest
        self._v2manifest = v2manifest

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
               self._v1manifest == other._v1manifest and \
               self._v2manifest == other._v2manifest

    def get_created_date(self):
        return self._v1manifest.get_created_date()

    def get_docker_version(self):
        return self._v1manifest.get_docker_version()

    def get_entrypoint(self):
        return self._v1manifest.get_entrypoint()

    def get_exposed_ports(self):
        return self._v1manifest.get_exposed_ports()

    def get_volumes(self):
        return self._v1manifest.get_volumes()

    def get_layer_ids(self):
        return self._v1manifest.get_layer_ids()

    def get_layers_count(self):
        return self._v2manifest.get_layers_count()

    def get_size(self):
        return self._v2manifest.get_size()


def make_manifest(content):
    if content['schemaVersion'] == 1:
        return DockerRegistrySchema1Manifest(content)
    elif content['schemaVersion'] == 2:
        return DockerRegistrySchema2Manifest(content)
    else:
        raise ValueError(
            f"Unsupported manifest schema version: {content['schemaVersion']}")
