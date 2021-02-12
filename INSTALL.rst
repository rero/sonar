..
    Swiss Open Access Repository
    Copyright (C) 2021 RERO

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, version 3 of the License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


Installation
------------

First, create your working directory and ``cd`` into it. Clone the project into this directory:

.. code-block:: console

    $ git clone https://github.com/rero/sonar.git

You need to install `poetry`, it will handle the virtual environment creation for the project
in order to sandbox our Python environment, as well as manage the dependency installation,
among other things.

.. code-block:: console

    $ pyenv install 3.6.10
    $ cd sonar
    $ pyenv local 3.6.10
    $ pip install poetry

Next, ``cd`` into the project directory and bootstrap the instance (this will install
all Python dependencies and build all static assets):

.. code-block:: console

    $ cd sonar
    $ poetry run ./scripts/bootstrap

Start all dependent services using docker-compose (this will start PostgreSQL,
Elasticsearch 6, RabbitMQ and Redis):

.. code-block:: console

    $ docker-compose up -d


Make sure you have `enough virtual memory
<https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html#docker-cli-run-prod-mode>`_
for Elasticsearch in Docker:

.. code-block:: shell

    # Linux
    $ sysctl -w vm.max_map_count=262144

    # macOS
    $ screen ~/Library/Containers/com.docker.docker/Data/com.docker.driver.amd64-linux/tty
    <enter>
    linut00001:~# sysctl -w vm.max_map_count=262144


Next, create database tables, search indexes and message queues:

.. code-block:: console

    $ poetry run ./scripts/setup

Running
-------
Start the webserver and the celery worker:

.. code-block:: console

    $ poetry run ./scripts/server

Start a Python shell:

.. code-block:: console

    $ poetry run ./scripts/console

Testing
-------
Run the test suite via the provided script:

.. code-block:: console

    $ poetry run ./scripts/test

By default, end-to-end tests are skipped. You can include the E2E tests like
this:

.. code-block:: console

    $ env E2E=yes poetry run ./scripts/test

For more information about end-to-end testing see `pytest-invenio
<https://pytest-invenio.readthedocs.io/en/latest/usage.html#running-e2e-tests>`_.


Production environment
----------------------
You can use simulate a full production environment using the
``docker-compose.full.yml``. You can start it like this:

.. code-block:: console

    $ ./docker/build-images.sh
    $ docker-compose -f docker-compose.full.yml up -d
    $ ./docker/wait-for-services.sh --full

Remember to create database tables, search indexes and message queues if not
already done:

.. code-block:: console

    $ docker-compose -f docker-compose.full.yml run --rm web-ui "poetry run ./scripts/setup"

In addition to the normal ``docker-compose.yml``, this one will start:

- HAProxy (load balancer)
- Nginx (web frontend)
- UWSGI (application container)
- Celery (background task worker)
- Celery (background task beat)
- Flower (Celery monitoring)



.. References:
.. _GitHub: https://github.com/rero/sonar
.. _Travis: https://travis-ci.org/rero/sonar
.. _Docker: https://hub.docker.com/r/rero/sonar/
.. _npm: https://www.npmjs.com/org/rero
.. _Gitter: https://gitter.im/rero/interne
.. _Weblate: https://hosted.weblate.org/projects/rero_plus/sonar/
