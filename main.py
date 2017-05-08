import argparse
import json

import flask

from docker_registry_frontend.registry import DockerV2Registry
from docker_registry_frontend.storage import STORAGE_DRIVERS


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
    registry_web.get_registry_by_name(registry).get_created_date('registry', '2')
    return flask.render_template('tag_overview.html',
                                 registry=registry_web.get_registry_by_name(registry),
                                 repo=repo)


@app.route('/registry/<registry>/repo/<repo>/tag/<tag>')
def tag_detail(registry, repo, tag):
    return flask.render_template('tag_detail.html',
                                 registry=registry_web.get_registry_by_name(registry),
                                 repo=repo,
                                 tag=tag
                                 )

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
