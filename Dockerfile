# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

ARG VERSION=latest
FROM sonar-base:${VERSION}

USER 0

# Copy files
COPY ./ ${WORKING_DIR}/src
WORKDIR ${WORKING_DIR}/src
COPY ./docker/uwsgi/ ${INVENIO_INSTANCE_PATH}

# Change owner
RUN chown -R invenio:invenio ${WORKING_DIR}

USER 1000

# Run bootstrap
ENV TERM=xterm-256color
# to avoid lxml conflict
ENV UWSGI_PROFILE_OVERRIDE="xml=no"
ARG UI_TGZ=""
ENV INVENIO_COLLECT_STORAGE='flask_collect.storage.file'
RUN uv run --no-sync ./scripts/bootstrap --deploy -t ${UI_TGZ}

ENTRYPOINT [ "bash", "-c"]
