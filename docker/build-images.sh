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
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


script_path=$(dirname "$0")

pipfile_lock_path="$script_path/../Pipfile.lock"

if [ ! -f $pipfile_lock_path ]; then
    echo "'Pipfile.lock' not found. Generate it by running 'pipenv lock'."
    exit 1
fi

# Extract Pipfile.lock hash to use as the docker image tag
deps_ver=$(cat $pipfile_lock_path | python -c "import json,sys;print(json.load(sys.stdin)['_meta']['hash']['sha256'])")

# Build dependencies image
docker build -f Dockerfile.base -t sonar-base:$deps_ver .

# Build application image
docker build --build-arg DEPENDENCIES_VERSION=$deps_ver . -t sonar
