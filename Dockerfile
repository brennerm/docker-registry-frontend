FROM tiangolo/uwsgi-nginx-flask:python3.8-alpine

ENV SOURCE_DIR /app
WORKDIR $SOURCE_DIR

COPY Dockerfile LICENSE requirements.txt bower.json .bowerrc main.py $SOURCE_DIR/

RUN apk add --no-cache \
      --virtual .build-deps \
      nodejs-npm \
      git \
      build-base && \
    pip install --no-cache-dir -r $SOURCE_DIR/requirements.txt && \
    npm install -g bower && \
    bower --allow-root install && \
    apk del .build-deps

COPY docker_registry_frontend/ $SOURCE_DIR/docker_registry_frontend
COPY static $SOURCE_DIR/static
COPY templates $SOURCE_DIR/templates

COPY ./uwsgi.ini $SOURCE_DIR/uwsgi.ini