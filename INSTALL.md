<!--
SPDX-FileCopyrightText: Fondation RERO+
SPDX-License-Identifier: AGPL-3.0-or-later
-->

# SONAR Installation

## Requirements

- `git`
- `docker`, `docker-compose`
- `uv`

## Installation

First, create your working directory and `cd` into it. Clone the project into this directory:

```console
git clone https://github.com/rero/sonar.git
```

You need to install `uv`, it will handle Python installation, the virtual environment
creation for the project in order to sandbox our Python environment, as well as manage
the dependency installation, among other things.

```console
curl -LsSf https://astral.sh/uv/install.sh | sh
cd sonar
uv python install 3.14
```

See the [uv installation documentation](https://docs.astral.sh/uv/getting-started/installation) for more detail.

Next, `cd` into the project directory and bootstrap the instance (this will install
all Python dependencies and build all static assets):

```console
cd sonar
uv run ./scripts/bootstrap
```

Start all dependent services using docker-compose (this will start PostgreSQL,
Elasticsearch 6, RabbitMQ and Redis):

```console
docker compose up -d
```

Make sure you have [enough virtual memory](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html#docker-cli-run-prod-mode)
for Elasticsearch in Docker:

```shell
# Linux
sysctl -w vm.max_map_count=262144

# macOS
screen ~/Library/Containers/com.docker.docker/Data/com.docker.driver.amd64-linux/tty
# press <enter>
linut00001:~# sysctl -w vm.max_map_count=262144
```

Next, create database tables, search indexes and message queues:

```console
uv run poe setup
```

## Running

Start the webserver and the celery worker:

```console
uv run poe server
```

Start a Python shell:

```console
uv run poe console
```

## Upgrading

In order to upgrade an existing instance simply run:

```console
uv run poe update
```

## Testing

Run the test suite via the provided script:

```console
uv run poe run_tests
```

By default, end-to-end tests are skipped.

## Production environment

You can simulate a full production environment using `docker-compose.full.yml`:

```console
./docker/build-images.sh
docker compose -f docker-compose.full.yml up -d
./docker/wait-for-services.sh --full
```

In addition to the normal `docker-compose.yml`, this one will start:

- HAProxy (load balancer)
- Nginx (web frontend)
- UWSGI (application container)
- Celery (background task worker)
- Celery (background task beat)
- Flower (Celery monitoring)
