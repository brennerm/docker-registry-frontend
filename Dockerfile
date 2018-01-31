FROM python:alpine3.6
MAINTAINER "xamrennerb@gmail.com"

ENV SOURCE_DIR /root
WORKDIR $SOURCE_DIR

COPY Dockerfile LICENSE requirements.txt bower.json .bowerrc config.json frontend.py $SOURCE_DIR/
COPY docker_registry_frontend/ $SOURCE_DIR/docker_registry_frontend
COPY static $SOURCE_DIR/static
COPY templates $SOURCE_DIR/templates

RUN apk update && \
    apk add \
      nginx \
      nodejs-npm \ 
      git && \
    pip install -r /root/requirements.txt && \
    npm install -g bower && \
    bower --allow-root install && \
    mkdir -p /run/nginx

COPY docker-registry-frontend.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
VOLUME ['/etc/nginx/sites-enabled/docker-registry-frontend.conf', '/root/config.json']

ENTRYPOINT python3 frontend.py -i 127.0.0.1 -p 8080 config.json & nginx -g "daemon off;"
