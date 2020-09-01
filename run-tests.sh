#!/usr/bin/env bash
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

# Ignoring false positive 36759 (reporting invenio-admin v1.0.1). This can be
# removed when https://github.com/pyupio/safety-db/pull/2274 is merged and
# released.

SCRIPT_PATH=$(dirname "$0")

# TODO: Use pipenv check when it will be available again
pipenv run safety check && \
pipenv run pydocstyle sonar tests docs && \
pipenv run isort --check-only --diff "${SCRIPT_PATH}" && \
pipenv run check-manifest --ignore ".travis-*,docs/_build*" && \
pipenv run sphinx-build -qnNW docs docs/_build/html && \
pipenv run test
