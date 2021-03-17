FROM tiangolo/uwsgi-nginx-flask:python3.8-alpine

ENV SOURCE_DIR /app
WORKDIR $SOURCE_DIR

COPY Dockerfile LICENSE requirements.txt bower.json .bowerrc main.py $SOURCE_DIR/
COPY docker_registry_frontend/ $SOURCE_DIR/docker_registry_frontend
COPY static $SOURCE_DIR/static
COPY templates $SOURCE_DIR/templates

RUN apk update && \
    apk add \
      nodejs-npm \
      git && \
    pip install -r $SOURCE_DIR/requirements.txt && \
    npm install -g bower && \
    bower --allow-root install
