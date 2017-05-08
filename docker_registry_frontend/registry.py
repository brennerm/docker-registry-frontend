import datetime
import json
import urllib.error
import urllib.request

from docker_registry_frontend.manifest import makeManifest


class DockerV2Registry:
    API_BASE = '{url}/v2'
    GET_ALL_REPOS_TEMPLATE = '{url}/v2/_catalog'
    GET_ALL_TAGS_TEMPLATE = '{url}/v2/{repo}/tags/list'
    GET_MANIFEST_TEMPLATE = '{url}/v2/{repo}/manifests/{tag}'
    GET_LAYER_TEMPLATE = '{url}/v2/{repo}/blobs/{digest}'

    def __init__(self, name, url, user=None, password=None):
        self.__name = name
        self.__url = url
        self.__user = user
        self.__password = password

    @property
    def name(self):
        return self.__name

    @property
    def url(self):
        return self.__url

    @staticmethod
    def json_request(*args, **kwargs):
        return json.loads(
            DockerV2Registry.request(*args, **kwargs).read().decode()
        )

    @staticmethod
    def request(*args, **kwargs):
        request = urllib.request.Request(*args, **kwargs)
        return urllib.request.urlopen(request)

    def get_manifest(self, repo, tag):
        return makeManifest(
            DockerV2Registry.json_request(
                DockerV2Registry.GET_MANIFEST_TEMPLATE.format(
                    url=self.__url,
                    repo=repo,
                    tag=tag
                )
            )
        )

    def is_online(self):
        try:
            resp = DockerV2Registry.request(DockerV2Registry.API_BASE.format(
                    url=self.__url
            ))
        except urllib.error.URLError:
            return False

        return True if resp.getcode() == 200 else False

    def get_repos(self):
        return DockerV2Registry.json_request(DockerV2Registry.GET_ALL_REPOS_TEMPLATE.format(
            url=self.__url)
        )['repositories']

    def get_number_of_repos(self):
            return len(self.get_repos())

    def get_tags(self, repo):
        tags = DockerV2Registry.json_request(DockerV2Registry.GET_ALL_TAGS_TEMPLATE.format(
            url=self.__url,
            repo=repo
        ))['tags']

        return tags

    def get_number_of_tags(self, repo):
        return len(self.get_tags(repo))

    def get_number_of_layers(self, repo, tag):
        return self.get_manifest(repo, tag).get_number_of_layers()

    def get_size_of_layers(self, repo, tag):
        layers = DockerV2Registry.json_request(
            DockerV2Registry.GET_MANIFEST_TEMPLATE.format(
                url=self.__url,
                repo=repo,
                tag=tag
            )
        )['fsLayers']

        result = 0

        for layer in layers:
            result += int(DockerV2Registry.request(
                DockerV2Registry.GET_LAYER_TEMPLATE.format(
                    url=self.__url,
                    repo=repo,
                    digest=layer['blobSum']
                ),
                method='HEAD'
            ).info()['Content-Length'])

        return result

    def get_created_date(self, repo, tag):
        return datetime.datetime.strptime(
            self.get_manifest(repo, tag).get_created_date().split('.')[0],  # ignore microseconds
            '%Y-%m-%dT%H:%M:%S'
        )

    def get_entrypoint(self, repo, tag):
        return self.get_manifest(repo, tag).get_entrypoint()

    def get_docker_version(self, repo, tag):
        return self.get_manifest(repo, tag).get_docker_version()

    def get_exposed_ports(self, repo, tag):
        return self.get_manifest(repo, tag).get_exposed_ports()

    def get_volumes(self, repo, tag):
        return self.get_manifest(repo, tag).get_volumes()
