import abc
import concurrent
import functools
import json
import re
import socket
import urllib.error
import urllib.request
import urllib.parse
import uuid
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Dict, Any

import requests
import requests_cache
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


from docker_registry_frontend.manifest import make_manifest, \
    DockerRegistryCombinedManifest


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

    @functools.lru_cache(maxsize=100)
    def supports_tag_deletion(self, repo):
        response = self.request(
                'DELETE',
                DockerV2Registry.GET_MANIFEST_TEMPLATE.format(
                    url=self._url,
                    repo=repo,
                    tag=str(uuid.uuid4())
                )
            )
        return False if response.status_code == 403 else True

    def json_request(self, url, **kwargs) -> Dict[str, Any]:
        return json.loads(
            self.string_request(url, **kwargs)
        )

    def string_request(self, url, **kwargs) -> str:
        return self.request('GET', url, **kwargs).content.decode()

    def request(self, method, url, **kwargs) -> requests.Response:
        r = requests.Request(method, url, **kwargs).prepare()
        r.prepare_auth((self._user, self._password))
        response = self._session.send(r, timeout=(10, 10))
        # Clear cache on successful deletion of a repo or tag
        if r.method == 'DELETE' and response.status_code in range(200, 300):
            requests_cache.core.clear()
        return response

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

    def get_number_of_layers_with_tag(self, repo, tag):
        return tag, len(self.get_layer_ids(repo, tag))

    def get_number_of_all_layers(self, repo):
        result = {}
        tags = self.get_tags(repo)
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_tag = (executor.submit(self.get_number_of_layers_with_tag, repo, tag) for tag in tags)
            for future in concurrent.futures.as_completed(future_to_tag):
                tag, count = future.result()
                result[tag] = count
        return result

    def get_layer_ids(self, repo, tag):
        raise NotImplementedError

    @functools.lru_cache(maxsize=5000)
    def get_size_of_layers(self, repo, tag):
        return self.get_manifest(repo, tag).get_size()

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

    @functools.lru_cache(maxsize=50)
    def get_size_of_repo(self, repo):
        result = 0

        for tag in self.get_tags(repo):
            result += self.get_size_of_layers(repo, tag)

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
    LINK_HEADER_PATTERN = r"(?<=<)(.*)(?=>)"
    version = 2

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


    def is_online(self):
        try:
            resp = self.request('GET', DockerV2Registry.API_BASE.format(
                    url=self._url
            ))
        except (urllib.error.URLError, socket.timeout):
            return False

        return True if resp.status_code == 200 else False

    def get_repos(self, url_template: str = GET_ALL_REPOS_TEMPLATE):
        # TODO: replace recursion with a loop
        response = self.request('GET', url_template.format(
            url=self._url)
        )

        repos = json.loads(response.content.decode())['repositories']
        if 'Link' in response.headers:
            next_repos_link = re.search(DockerV2Registry.LINK_HEADER_PATTERN, 
                                        response.headers['Link'])[0]
            repos += self.get_repos(next_repos_link)

        return repos

    @functools.lru_cache(maxsize=1000)
    def get_tags(self, repo):
        tags = self.json_request(DockerV2Registry.GET_ALL_TAGS_TEMPLATE.format(
            url=self._url,
            repo=repo
        ))['tags']

        return tags or []

    def get_layer_ids(self, repo, tag):
        return self.get_manifest(repo, tag).get_layer_ids()

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
