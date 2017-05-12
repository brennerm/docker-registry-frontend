# docker-registry-frontend
Web front end to display the content of multiple Docker registries

![Build Status](https://travis-ci.org/brennerm/docker-registry-frontend.svg?branch=master)

## Feature Overview
- browse available Docker images and check the availability of multiple Docker registries
- add and remove registries via the web interface
- get detailed information about your Docker images

## Installation
```
$ git clone git@github.com:brennerm/docker-registry-frontend.git && cd docker-registry-frontend
$ pip3 install -r requirements.txt
```

## Usage
```
$ python3 main.py -h
usage: main.py [-h] [-d] [-i IP_ADDRESS] [-p PORT] config

positional arguments:
  config

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           Run application in debug mode
  -i IP_ADDRESS, --ip-address IP_ADDRESS IP address to bind application to
  -p PORT, --port PORT  Port to bind application to

$ python3 main.py config.json
```

## Configuration
### Supported storage drivers
The frontend supports various kinds of storages to persists the configuration.
The following options are currently implemented:
- SQLite
```
{
  "storage": {
    "driver": "sqlite",
    "file_path": "db.sqlite" # Use ":memory:" to use an in-memory database.
  }
}
```
- JSON File
```
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
