import abc
import functools
import json
import socket
import urllib.error
import urllib.request
import urllib.parse

from docker_registry_frontend.manifest import makeManifest
from docker_registry_frontend.cache import cache_with_timeout

def nested_get(dictionary, *keys, default=None):
    return functools.reduce(lambda el, key: el.get(key) if el else default, keys, dictionary)


class DockerRegistry(abc.ABC):
    version = None

    def __init__(self, name, url, user=None, password=None):
        self._name = name
        self._url = url
        self._user = user
        self._password = password

    def __key(self):
        return self._url

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @property
    def name(self):
        return self._name

    @property
    def url(self):
        return self._url

    @property
    def supports_repo_deletion(self):
        return False

    @property
    def supports_tag_deletion(self):
        return False

    @staticmethod
    def json_request(*args, **kwargs):
        return json.loads(
            DockerRegistry.string_request(*args, **kwargs)
        )

    @staticmethod
    @cache_with_timeout(1)  # enable caching to improve performance of multiple consecutive calls
    def string_request(*args, **kwargs):
        return DockerRegistry.request(*args, **kwargs).read().decode()

    @staticmethod
    def request(*args, **kwargs):
        request = urllib.request.Request(*args, **kwargs)
        return urllib.request.urlopen(request, timeout=3)

    def delete_repo(self, repo):
        raise NotImplementedError

    def delete_tag(self, repo, tag):
        raise NotImplementedError

    def is_online(self):
        raise NotImplementedError

    def get_repos(self):
        raise NotImplementedError

    def get_number_of_repos(self):
        return len(self.get_repos())

    def get_tags(self, repo):
        raise NotImplementedError

    def get_number_of_tags(self, repo):
        return len(self.get_tags(repo))

    def get_number_of_layers(self, repo, tag):
        return len(self.get_layer_ids(repo, tag))

    def get_layer_ids(self, repo, tag):
        raise NotImplementedError

    def get_size_of_layers(self, repo, tag):
        result = 0

        for image_id in self.get_layer_ids(repo, tag):
            result += self.get_size_of_layer(repo, image_id)

        return result

    def get_size_of_layer(self, repo, tag):
        raise NotImplementedError

    def get_size_of_repo(self, repo):
        result = 0

        for tag in self.get_tags(repo):
            result += self.get_size_of_layers(repo, tag)

        return result

    def get_size_of_registry(self):
        result = 0

        for repo in self.get_repos():
            result += self.get_size_of_repo(repo)

        return result

    def get_created_date(self, repo, tag):
        raise NotImplementedError

    def get_entrypoint(self, repo, tag):
        raise NotImplementedError

    def get_docker_version(self, repo, tag):
        raise NotImplementedError

    def get_exposed_ports(self, repo, tag):
        raise NotImplementedError

    def get_volumes(self, repo, tag):
        raise NotImplementedError


class DockerV1Registry(DockerRegistry):
    ONLINE_TEMPLATE = '{url}/v1/_ping'
    GET_ALL_REPOS_TEMPLATE = '{url}/v1/search'
    GET_ALL_TAGS_TEMPLATE = '{url}/v1/repositories/{repo}/tags'
    DELETE_REPO_TEMPLATE = '{url}/v1/repositories/{repo}/'
    DELETE_TAG_TEMPLATE = '{url}/v1/repositories/{repo}/tags/{tag}'
    GET_IMAGE_ID_TEMPLATE = GET_ALL_TAGS_TEMPLATE + '/{tag}'
    GET_IMAGE_TEMPLATE = '{url}/v1/images/{image_id}/json'
    GET_IMAGE_ANCESTORS = '{url}/v1/images/{image_id}/ancestry'
    GET_LAYER_TEMPLATE = '{url}/v1/images/{image_id}/layer'

    version = 1

    def __get_image_id(self, repo, tag):
        return DockerRegistry.string_request(DockerV1Registry.GET_IMAGE_ID_TEMPLATE.format(
            url=self._url,
            repo=repo,
            tag=tag
        )).replace('"', '')

    def __get_image(self, repo, tag):
        image_id = self.__get_image_id(repo, tag)

        return DockerRegistry.json_request(DockerV1Registry.GET_IMAGE_TEMPLATE.format(
            url=self._url,
            image_id=image_id
        ))

    @property
    def supports_repo_deletion(self):
        return True

    @property
    def supports_tag_deletion(self):
        return True

    def delete_repo(self, repo):
        DockerRegistry.request(
            DockerV1Registry.DELETE_REPO_TEMPLATE.format(
                url=self._url,
                repo=repo,
            ),
            method='DELETE'
        )

    def delete_tag(self, repo, tag):
        DockerRegistry.request(
            DockerV1Registry.DELETE_TAG_TEMPLATE.format(
                url=self._url,
                repo=repo,
                tag=tag
            ),
            method='DELETE'
        )

    def get_size_of_layer(self, repo, image_id):
        return int(DockerRegistry.request(DockerV1Registry.GET_LAYER_TEMPLATE.format(
            url=self._url,
            image_id=image_id
        )).info()['Content-Length'])

    def get_tags(self, repo):
        return DockerRegistry.json_request(DockerV1Registry.GET_ALL_TAGS_TEMPLATE.format(
            url=self._url,
            repo=repo
        )).keys()

    def get_exposed_ports(self, repo, tag):
        return nested_get(self.__get_image(repo, tag), 'container_config', 'ExposedPorts')

    def get_repos(self):
        return [result['name'] for result in DockerRegistry.json_request(DockerV1Registry.GET_ALL_REPOS_TEMPLATE.format(
            url=self._url)
        )['results']]

    def get_docker_version(self, repo, tag):
        return self.__get_image(repo, tag).get('docker_version')

    def get_layer_ids(self, repo, tag):
        image_id = self.__get_image_id(repo, tag)

        return DockerRegistry.json_request(DockerV1Registry.GET_IMAGE_ANCESTORS.format(
            url=self._url,
            image_id=image_id
        ))

    def is_online(self):
        try:
            resp = DockerRegistry.request(DockerV1Registry.ONLINE_TEMPLATE.format(
                    url=self._url
            ))
        except (urllib.error.URLError, socket.timeout):
            return False

        return True if resp.getcode() == 200 else False

    def get_volumes(self, repo, tag):
        return nested_get(self.__get_image(repo, tag), 'container_config', 'Volumes')

    def get_entrypoint(self, repo, tag):
        return nested_get(self.__get_image(repo, tag), 'container_config', 'Entrypoint')

    def get_created_date(self, repo, tag):
        return self.__get_image(repo, tag).get('created')


class DockerV2Registry(DockerRegistry):
    API_BASE = '{url}/v2'
    GET_ALL_REPOS_TEMPLATE = '{url}/v2/_catalog'
    GET_ALL_TAGS_TEMPLATE = '{url}/v2/{repo}/tags/list'
    GET_MANIFEST_TEMPLATE = '{url}/v2/{repo}/manifests/{tag}'
    GET_LAYER_TEMPLATE = '{url}/v2/{repo}/blobs/{digest}'

    version = 2

    @property
    def supports_tag_deletion(self):
        try:
            DockerRegistry.request(
                DockerV2Registry.GET_MANIFEST_TEMPLATE.format(
                    url=self._url,
                    repo='foo',
                    tag='bar'
                ),
                method='DELETE'
            )
        except urllib.error.HTTPError as e:
            if e.code == 405:
                return False
            else:
                return True

    def delete_tag(self, repo, tag):
        digest = DockerRegistry.request(
            DockerV2Registry.GET_MANIFEST_TEMPLATE.format(
                url=self._url,
                repo=repo,
                tag=tag
            ),
            method='HEAD',
            headers={'Accept': 'application/vnd.docker.distribution.manifest.v2+json'}
        ).info()['Docker-Content-Digest']

        try:
            DockerRegistry.request(
                DockerV2Registry.GET_MANIFEST_TEMPLATE.format(
                    url=self._url,
                    repo=repo,
                    tag=digest
                ),
                method='DELETE'
            )
        except urllib.error.HTTPError:
            raise

    @cache_with_timeout()
    def get_manifest(self, repo, tag):
        return makeManifest(
            DockerRegistry.json_request(
                DockerV2Registry.GET_MANIFEST_TEMPLATE.format(
                    url=self._url,
                    repo=repo,
                    tag=tag
                )
            )
        )

    def is_online(self):
        try:
            resp = DockerRegistry.request(DockerV2Registry.API_BASE.format(
                    url=self._url
            ))
        except (urllib.error.URLError, socket.timeout):
            return False

        return True if resp.getcode() == 200 else False

    def get_repos(self):
        return DockerRegistry.json_request(DockerV2Registry.GET_ALL_REPOS_TEMPLATE.format(
            url=self._url)
        )['repositories']

    def get_tags(self, repo):
        tags = DockerRegistry.json_request(DockerV2Registry.GET_ALL_TAGS_TEMPLATE.format(
            url=self._url,
            repo=repo
        ))['tags']

        return tags or []

    def get_layer_ids(self, repo, tag):
        return self.get_manifest(repo, tag).get_layer_ids()

    @cache_with_timeout()
    def get_size_of_layer(self, repo, layer_id):
        return int(DockerRegistry.request(
                DockerV2Registry.GET_LAYER_TEMPLATE.format(
                    url=self._url,
                    repo=repo,
                    digest=layer_id
                ),
                method='HEAD'
            ).info()['Content-Length'])

    def get_created_date(self, repo, tag):
        return self.get_manifest(repo, tag).get_created_date()

    def get_entrypoint(self, repo, tag):
        return self.get_manifest(repo, tag).get_entrypoint()

    def get_docker_version(self, repo, tag):
        return self.get_manifest(repo, tag).get_docker_version()

    def get_exposed_ports(self, repo, tag):
        return self.get_manifest(repo, tag).get_exposed_ports()

    def get_volumes(self, repo, tag):
        return self.get_manifest(repo, tag).get_volumes()


def make_registry(*args, **kwargs):
    v2registry = DockerV2Registry(*args, **kwargs)
    v1registry = DockerV1Registry(*args, **kwargs)

    if v2registry.is_online():
        return v2registry
    elif v1registry.is_online():
        return v1registry
    else:
        return v2registry
