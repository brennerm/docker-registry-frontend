import abc
import base64
import functools
import json
import socket
import urllib.error
import urllib.request
import urllib.parse
from typing import Dict, Any

import logging

logging.basicConfig(level=logging.DEBUG)

import requests
from requests_toolbelt.auth.handler import AuthHandler
from requests_toolbelt.utils import dump
import requests_cache
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


from docker_registry_frontend.manifest import make_manifest, \
    DockerRegistryCombinedManifest
from docker_registry_frontend.cache import cache_with_timeout


def nested_get(dictionary, *keys, default=None):
    return functools.reduce(lambda el, key: el.get(key) if el else default, keys, dictionary)


class DockerRegistry(abc.ABC):
    version = None

    def __init__(self, name, url, user=None, password=None):
        self._name = name
        self._url = url if url.startswith('http') else 'http://' + url
        self._user = user
        self._password = password
        self._session = requests.Session()

        # Cache responses for 5 minutes
        requests_cache.install_cache('requests', expire_after=300, include_get_headers=True)

        # Add retries
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)

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
    def user(self):
        return self._user

    @property
    def password(self):
        return self._password

    @property
    def supports_repo_deletion(self):
        return False

    @property
    def supports_tag_deletion(self):
        return False

    def json_request(self, url, **kwargs) -> Dict[str, Any]:
        return json.loads(
            self.string_request(url, **kwargs)
        )

    @cache_with_timeout(1)  # enable caching to improve performance of multiple consecutive calls
    def string_request(self, url, **kwargs) -> str:
        return self.request('GET', url, **kwargs).content.decode()

    def request(self, method, url, **kwargs) -> requests.Response:
        r = requests.Request(method, url, **kwargs).prepare()
        r.prepare_auth((self._user, self._password))
        response = self._session.send(r, timeout=(10, 10))
        # data = dump.dump_all(response)
        # print(data.decode('utf-8'))
        # Clear cache on successfull deletion of a repo or tag
        if r.method == 'DELETE' and response.status_code in range(200,300):
            requests_cache.core.clear()
        return response

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
        return self.get_manifest(repo, tag).get_size()

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


class DockerV2Registry(DockerRegistry):

    API_BASE = '{url}/v2/'
    GET_ALL_REPOS_TEMPLATE = '{url}/v2/_catalog'
    GET_ALL_TAGS_TEMPLATE = '{url}/v2/{repo}/tags/list'
    GET_MANIFEST_TEMPLATE = '{url}/v2/{repo}/manifests/{tag}'
    GET_LAYER_TEMPLATE = '{url}/v2/{repo}/blobs/{digest}'

    version = 2

    @property
    @functools.lru_cache(maxsize=2)
    def supports_tag_deletion(self):
        try:
            self.request(
                'DELETE',
                DockerV2Registry.GET_MANIFEST_TEMPLATE.format(
                    url=self._url,
                    repo='foo',
                    tag='bar'
                )
            )
        except urllib.error.HTTPError as e:
            if e.code == 405:
                return False
            else:
                return True

    def delete_tag(self, repo, tag):
        digest = self.request(
            'HEAD',
            DockerV2Registry.GET_MANIFEST_TEMPLATE.format(
                url=self._url,
                repo=repo,
                tag=tag
            ),
            headers={'Accept': 'application/vnd.docker.distribution.manifest.v2+json'}
        ).headers['Docker-Content-Digest']

        try:
            self.request(
                'DELETE',
                DockerV2Registry.GET_MANIFEST_TEMPLATE.format(
                    url=self._url,
                    repo=repo,
                    tag=digest
                )
            )
        except urllib.error.HTTPError:
            raise

    def delete_repo(self, repo):
        pass

    # @cache_with_timeout()
    @functools.lru_cache(maxsize=1000)
    def get_manifest(self, repo, tag):
        v1manifest = make_manifest(
            self.json_request(
                DockerV2Registry.GET_MANIFEST_TEMPLATE.format(
                    url=self._url,
                    repo=repo,
                    tag=tag
                )
            )
        )
        v2manifest = make_manifest(
            self.json_request(
                DockerV2Registry.GET_MANIFEST_TEMPLATE.format(
                    url=self._url,
                    repo=repo,
                    tag=tag
                ),
                headers = {"Accept": "application/vnd.docker.distribution.manifest.v2+json"}
            )
        )
        return DockerRegistryCombinedManifest(v1manifest, v2manifest)

    def is_online(self):
        try:
            resp = self.request('GET', DockerV2Registry.API_BASE.format(
                    url=self._url
            ))
        except (urllib.error.URLError, socket.timeout):
            return False

        return True if resp.status_code == 200 else False

    def get_repos(self):
        return self.json_request(DockerV2Registry.GET_ALL_REPOS_TEMPLATE.format(
            url=self._url)
        )['repositories']

    def get_tags(self, repo):
        tags = self.json_request(DockerV2Registry.GET_ALL_TAGS_TEMPLATE.format(
            url=self._url,
            repo=repo
        ))['tags']

        return tags or []

    def get_layer_ids(self, repo, tag):
        return self.get_manifest(repo, tag).get_layer_ids()

    @cache_with_timeout()
    def get_size_of_layer(self, repo, tag):
        manifest =  self.get_manifest(repo, tag)
        return 100
        # TODO Fix
        # return self.get_manifest(repo, layer_id)

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
    return DockerV2Registry(*args, **kwargs)
