#!/usr/bin/env bash
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

lock_file="$(dirname "$0")/../uv.lock"


if [ ! -f $lock_file ]; then
    echo "Lock file not found. Generate it by running 'uv sync'."
    exit 1
fi

# Extract uv.lock hash to use as the docker image tag
deps_ver="$(sed -n 's/content-hash = "\(.*\)"/\1/p' $lock_file)"

# Build dependencies image
docker build -f Dockerfile.base -t sonar-base:$deps_ver .

# Build application image
docker build --build-arg VERSION=$deps_ver . -t sonar
