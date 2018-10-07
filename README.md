# docker-registry-frontend
Web front end to display the content of multiple Docker registries

[![Build Status](https://travis-ci.org/brennerm/docker-registry-frontend.svg?branch=master)](https://travis-ci.org/brennerm/docker-registry-frontend)
[![Docker Build Status](https://img.shields.io/docker/build/brennerm/docker-registry-frontend.svg)](https://hub.docker.com/r/brennerm/docker-registry-frontend/)

## Feature Overview
- browse available Docker images and check the availability of multiple Docker registries
- add and remove registries via the web interface
- delete repositories and tags (automatically detected if registry supports it)
- support for Docker registries V1 and V2
- get detailed information about your Docker images
- supports Basic Auth protected registries

## Installation
```
$ git clone git@github.com:brennerm/docker-registry-frontend.git && cd docker-registry-frontend
$ pip3 install -r requirements.txt
$ bower install
```

## Usage
```
$ python3 frontend.py -h
usage: frontend.py [-h] [-d] [-i IP_ADDRESS] [-p PORT] config

positional arguments:
  config

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           Run application in debug mode
  -i IP_ADDRESS, --ip-address IP_ADDRESS IP address to bind application to
  -p PORT, --port PORT  Port to bind application to

$ python3 frontend.py config.json
```

Alternatively you can use the prebuilt Docker image.
```
docker run -d -p 127.0.0.1:80:80 brennerm/docker-registry-frontend
```
This makes the front end available at http://127.0.0.1:80.

## Configuration
### Caching
It's possible to enable a caching functionality to keep the frontend fast even when viewing thousands of repos and tags.
By default it's disabled as there is no need for small registries. To enable it set a value for the cache timeout in seconds.
```json
{
  "cache_timeout": 3600
}
```
### Supported storage drivers
The frontend supports various kinds of storages to persists the configuration.
The following options are currently implemented:
- SQLite
```json
{
  "storage": {
    "driver": "sqlite",
    "file_path": "db.sqlite"
  }
}
```
 Set the "file_path" value to ":memory:" to use an in-memory database.

- JSON File
```json
{
  "storage": {
    "driver": "json",
    "file_path": "db.json"
  }
}
```

If you'd like to use another storage feel free to create an issue or open a pull request.

## Images
### Registry Overview
![Registry Overview](/img/registry_overview.png)

### Repository Overview
![Repository Overview](/img/repo_overview.png)

### Tag Overview
![Tag Overview](/img/tag_overview.png)

### Tag Detail
![Tag Detail](/img/tag_detail.png)
