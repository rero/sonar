# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2019 RERO
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Dockerfile that builds a fully functional image of your app.
#
# Note: It is important to keep the commands in this file in sync with your
# boostrap script located in ./scripts/bootstrap.
#
# In order to increase the build speed, we are extending this image from a base
# image (built with Dockerfile.base) which only includes your Python
# dependencies.

ARG DEPENDENCIES_VERSION=latest
FROM sonar-base:${DEPENDENCIES_VERSION}

COPY ./ .
COPY ./docker/uwsgi/ ${INVENIO_INSTANCE_PATH}

RUN pip install . && \
    invenio collect -v  && \
    invenio webpack create && \
    # --unsafe needed because we are running as root
    invenio webpack install --unsafe && \
    invenio webpack build &&  \
    invenio utils compile-json ./sonar/modules/documents/jsonschemas/documents/document-v1.0.0_src.json -o ./sonar/modules/documents/jsonschemas/documents/document-v1.0.0.json && \
    python ./setup.py compile_catalog && \
    pip install . && \
    mkdir ${INVENIO_INSTANCE_PATH}/static/sonar-ui && \
    cp ${INVENIO_INSTANCE_PATH}/assets/node_modules/@rero/sonar-ui/dist/sonar/* ${INVENIO_INSTANCE_PATH}/static/sonar-ui

ENTRYPOINT [ "bash", "-c"]
