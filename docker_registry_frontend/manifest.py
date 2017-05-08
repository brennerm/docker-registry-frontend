import abc
import json


class DockerRegistryManifest(abc.ABC):
    def __init__(self, content):
        self._content = content

    def get_number_of_layers(self):
        raise NotImplementedError

    def get_created_date(self):
        raise NotImplementedError


class DockerRegistrySchema1Manifest(DockerRegistryManifest):
    def get_created_date(self):
        created = []
        for entry in self._content['history']:
            created.append(json.loads(entry['v1Compatibility'])['created'])

        return sorted(created, reverse=True)[0]

    def get_number_of_layers(self):
        return len(self._content['fsLayers'])


def makeManifest(content):
    if content['schemaVersion'] == 1:
        return DockerRegistrySchema1Manifest(content)
    else:
        raise ValueError
