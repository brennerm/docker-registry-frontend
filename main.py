import argparse
import asyncio
import ssl
import urllib.parse

import flask

from docker_registry_frontend.config import create_config as create_config
from docker_registry_frontend.storage import DockerRegistryJsonFileStorage

ssl._create_default_https_context = ssl._create_unverified_context


class DockerRegistryWeb:
    def __init__(self, storage):
        self.__storage = storage

    @property
    def registries(self):
        return self.__storage.get_registries()

    def get_registry(self, identifier):
        for key, registry in self.registries.items():
            print(key, identifier)
            if key == identifier:
                return registry

        raise KeyError

    def get_registry_by_name(self, name):
        for registry in self.registries.values():
            if registry.name == name:
                return registry

        raise KeyError


asyncio.get_event_loop().run_until_complete(create_config())

app = flask.Flask(__name__)
registry_web_storage = DockerRegistryJsonFileStorage("db.json")
registry_web = DockerRegistryWeb(registry_web_storage)


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


@app.route('/delete_tag', methods=['POST'])
def delete_tag():
    registry = registry_web.get_registry_by_name(
        flask.request.args.get('registry_name'))
    repo = flask.request.args.get('repo')
    tag = flask.request.args.get('tag')

    registry.delete_tag(repo, tag)

    return flask.redirect(
        flask.url_for('tag_overview', registry_name=registry.name, repo=repo))


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
    argparser.add_argument('-d', '--debug', help='Run application in debug mode',
                           action='store_true', default=False)
    argparser.add_argument('-i', '--ip-address',
                           help='IP address to bind application to', default='0.0.0.0')
    argparser.add_argument('-p', '--port', help='Port to bind application to',
                           default=8080, type=int)
    arguments = argparser.parse_args()

    app.run(
        debug=arguments.debug,
        host=arguments.ip_address,
        port=arguments.port
    )
