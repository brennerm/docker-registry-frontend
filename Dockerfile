FROM ubuntu:xenial
MAINTAINER "xamrennerb@gmail.com"

ENV SOURCE_DIR /root

COPY Dockerfile $SOURCE_DIR
COPY LICENSE $SOURCE_DIR
COPY requirements.txt $SOURCE_DIR
COPY bower.json $SOURCE_DIR
COPY .bowerrc $SOURCE_DIR
COPY config.json $SOURCE_DIR
COPY docker_registry_frontend $SOURCE_DIR/docker_registry_frontend
COPY static $SOURCE_DIR/static
COPY templates $SOURCE_DIR/templates
COPY frontend.py $SOURCE_DIR

WORKDIR $SOURCE_DIR

RUN apt-get update && \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get -y install \
      git \
      nginx \
      npm \
      python3 \
      python3-pip \
      --no-install-recommends && \
    pip3 install setuptools wheel && \
    pip3 install -r /root/requirements.txt && \
    ln -s /usr/bin/nodejs /usr/bin/node && \
    npm install -g bower && \
    bower --allow-root install && \
    apt-get -y purge git npm python3-pip && \
    apt-get -y autoremove && \
    apt-get -y clean && \
    rm -rf /var/lib/apt/lists/* &&\
    rm /etc/nginx/sites-enabled/default

COPY docker-registry-frontend.conf /etc/nginx/sites-available/
RUN ln -s /etc/nginx/sites-available/docker-registry-frontend.conf /etc/nginx/sites-enabled/docker-registry-frontend.conf

EXPOSE 80
VOLUME ['/etc/nginx/sites-enabled/docker-registry-frontend.conf', '/root/config.json']

ENTRYPOINT service nginx start && python3 frontend.py -i 127.0.0.1 -p 8080 config.json
