# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2021 RERO
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

ARG VERSION=latest
FROM sonar-base:${VERSION}

# Copy files
COPY ./ ${WORKING_DIR}/src
WORKDIR ${WORKING_DIR}/src
COPY ./docker/uwsgi/ ${INVENIO_INSTANCE_PATH}

# Change owner
RUN chown -R invenio:invenio ${WORKING_DIR}

# Run bootstrap
ENV TERM=xterm-256color
ARG UI_TGZ=""
RUN poetry run ./scripts/bootstrap --deploy --ui ${UI_TGZ}

ENTRYPOINT [ "bash", "-c"]
