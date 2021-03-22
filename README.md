# docker-registry-frontend
Web front end to display the content of a Docker registry

## Feature Overview
- browse available Docker images
- delete tags (automatically detected if registry supports it)
- get detailed information about your Docker images
- supports Basic Auth protected registries

## Running

```bash
neuro run --pass-config --http 80 neuromation/docker-registry-frontend
```
