import argparse
import abc
import json
import os
import sqlite3
import urllib.request
import urllib.error

import flask


class DockerRegistryWebStorage(abc.ABC):
    def get_registries(self):
        raise NotImplementedError

    def add_registry(self, name, url, user=None, password=None):
        raise NotImplementedError

    def remove_registry(self, name):
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

    def add_registry(self, name, url, user=None, password=None):
        registries = self.__read()

        registries[name] = {
            'url': url,
            'user': user,
            'password': password
        }

        self.__write(registries)

    def remove_registry(self, name):
        registries = self.__read()
        if name in registries:
            registries.pop(name)

        self.__write(registries)

    def get_registries(self):
        registries = []
        for name, config in self.__read().items():
            registries.append(
                DockerV2Registry(
                    name,
                    config['url'],
                    config.get('user', None),
                    config.get('password', None)
                )
            )

        return registries


class DockerRegistrySQLiteStorage(DockerRegistryWebStorage):
    def __init__(self, file_path, *args, **kwargs):
        self.__sqlite_file = file_path
        self.__conn = sqlite3.connect(file_path, check_same_thread=False)

        cursor = self.__conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS registries (id INTEGER PRIMARY KEY, name TEXT NOT NULL, url TEXT NOT NULL, user TEXT, password TEXT);")

    def __execute(self, *args, **kwargs):
        cursor = self.__conn.cursor()
        res = cursor.execute(*args, **kwargs)

        self.__conn.commit()
        return res

    def add_registry(self, name, url, user=None, password=None):
        self.__execute('INSERT INTO registries (name, url, user, password) VALUES (:name, :url, :user, :password);',
                       {'name': name, 'url': url, 'user': user, 'password': password})

    def remove_registry(self, name):
        self.__execute('DELETE FROM registries WHERE name = :name;', {'name': name})

    def get_registries(self):
        registries = []

        for row in self.__execute('SELECT * FROM registries;'):
            _, name, url, user, password = row
            registries.append(
                DockerV2Registry(
                    name,
                    url,
                    user,
                    password
                )
            )

        return registries

STORAGE_DRIVERS = {
    'sqlite': DockerRegistrySQLiteStorage,
    'json': DockerRegistryJsonFileStorage
}


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
        return len(DockerV2Registry.json_request(
            DockerV2Registry.GET_MANIFEST_TEMPLATE.format(
                url=self.__url,
                repo=repo,
                tag=tag
            )
        )['fsLayers'])

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


class DockerRegistryWeb:
    def __init__(self, storage):
        self.__storage = storage

    @property
    def registries(self):
        return self.__storage.get_registries()

    def get_registry_by_name(self, name):
        for registry in self.registries:
            if registry.name == name:
                return registry

        raise KeyError

    def add_registry(self, name, url, user=None, password=None):
        self.__storage.add_registry(name, url, user, password)

    def remove_registry(self, name):
        self.__storage.remove_registry(name)

app = flask.Flask(__name__)


@app.route('/')
def registry_overview():
    return flask.render_template('registry_overview.html',
                                 registries=registry_web.registries)


@app.route('/test_connection')
def test_registry_connection():
    url = flask.request.args.get('url')
    if DockerV2Registry(None, url).is_online():
        return '', 200
    else:
        return '', 400


@app.route('/add_registry', methods=['GET', 'POST'])
def add_registry():
    if flask.request.method == 'GET':
        return flask.render_template('add_registry.html')
    elif flask.request.method == 'POST':
        registry_web.add_registry(
            flask.request.form['name'],
            flask.request.form['url'],
            flask.request.form.get('user', None),
            flask.request.form.get('password', None)
        )

        return flask.redirect(flask.url_for('registry_overview'))


@app.route('/remove_registry', methods=['POST'])
def remove_registry():
    registry_web.remove_registry(
        flask.request.args.get('name')
    )

    return flask.redirect(flask.url_for('registry_overview'))


@app.route('/registry/<registry>')
def repo_overview(registry):
    return flask.render_template('repo_overview.html',
                                 registry=registry_web.get_registry_by_name(registry))


@app.route('/registry/<registry>/repo/<repo>')
def tag_overview(registry, repo):
    return flask.render_template('tag_overview.html',
                                 registry=registry_web.get_registry_by_name(registry),
                                 repo=repo)

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('config')
    argparser.add_argument('-d', '--debug', help='Run application in debug mode', action='store_true', default=False)
    arguments = argparser.parse_args()

    with open(arguments.config, 'r') as config_file:
        config = json.load(config_file)

    registry_web_storage = STORAGE_DRIVERS[config['storage']['driver']](
        **config['storage']
    )

    registry_web = DockerRegistryWeb(registry_web_storage)
    app.run(debug=arguments.debug)
