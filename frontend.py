#!/usr/bin/env python3

import argparse
import json
import urllib.parse

import flask

from docker_registry_frontend.cache import cache_with_timeout
from docker_registry_frontend.registry import make_registry
from docker_registry_frontend.storage import STORAGE_DRIVERS


class DockerRegistryWeb:
    def __init__(self, storage):
        self.__storage = storage

    @property
    def registries(self):
        return self.__storage.get_registries()

    def get_registry_by_name(self, name):
        for registry in self.registries.values():
            if registry.name == name:
                return registry

        raise KeyError

    def add_registry(self, name, url, user=None, password=None):
        self.__storage.add_registry(name, url, user, password)

    def remove_registry(self, name):
        self.__storage.remove_registry(name)

app = flask.Flask(__name__)


@app.template_filter('to_mb')
def to_mb_filter_filter(value):
    return '%0.2f' % (value / 1024 ** 2)


@app.template_filter('urlencode')
def urlencode_filter(value):
    return urllib.parse.quote(value, safe='')


@app.template_filter('urldecode')
def urldecode_filter(value):
    return urllib.parse.unquote(value)


@app.route('/')
def registry_overview():
    return flask.render_template('registry_overview.html',
                                 registries=registry_web.registries)


@app.route('/test_connection')
def test_registry_connection():
    url = flask.request.args.get('url')

    try:
        if url and make_registry(None, url).is_online():
            return '', 200
        else:
            return '', 400
    except ValueError:
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
        flask.request.args.get('id')
    )

    return flask.redirect(flask.url_for('registry_overview'))


@app.route('/delete_repo', methods=['POST'])
def delete_repo():
    registry = registry_web.get_registry_by_name(flask.request.args.get('registry_name'))
    repo = flask.request.args.get('repo')

    registry.delete_repo(urldecode_filter(repo))

    return flask.redirect(flask.url_for('repo_overview', registry_name=registry.name))


@app.route('/delete_tag', methods=['POST'])
def delete_tag():
    registry = registry_web.get_registry_by_name(flask.request.args.get('registry_name'))
    repo = flask.request.args.get('repo')
    tag = flask.request.args.get('tag')

    registry.delete_tag(repo, tag)

    return flask.redirect(flask.url_for('tag_overview', registry_name=registry.name, repo=repo))


@app.route('/registry/<registry_name>')
def repo_overview(registry_name):
    try:
        registry = registry_web.get_registry_by_name(registry_name)
    except KeyError:
        flask.abort(404)

    return flask.render_template('repo_overview.html',
                                 registry=registry)


@app.route('/registry/<registry_name>/repo/<repo>')
def tag_overview(registry_name, repo):
    try:
        registry = registry_web.get_registry_by_name(registry_name)
    except KeyError:
        flask.abort(404)

    return flask.render_template('tag_overview.html',
                                 registry=registry,
                                 repo=urldecode_filter(repo))


@app.route('/registry/<registry_name>/repo/<repo>/tag/<tag>')
def tag_detail(registry_name, repo, tag):
    try:
        registry = registry_web.get_registry_by_name(registry_name)
    except KeyError:
        flask.abort(404)

    return flask.render_template('tag_detail.html',
                                 registry=registry,
                                 repo=urldecode_filter(repo),
                                 tag=tag
                                 )

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('config')
    argparser.add_argument('-d', '--debug', help='Run application in debug mode', action='store_true', default=False)
    argparser.add_argument('-i', '--ip-address', help='IP address to bind application to', default='0.0.0.0')
    argparser.add_argument('-p', '--port', help='Port to bind application to', default=8080, type=int)
    arguments = argparser.parse_args()

    with open(arguments.config, 'r') as config_file:
        config = json.load(config_file)

    cache_with_timeout.DEFAULT_TIMEOUT = config.get('cache_timeout', 0)

    registry_web_storage = STORAGE_DRIVERS[config['storage']['driver']](
        **config['storage']
    )

    registry_web = DockerRegistryWeb(registry_web_storage)
    app.run(
        debug=arguments.debug,
        host=arguments.ip_address,
        port=arguments.port
    )
