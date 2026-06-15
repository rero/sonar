#!/usr/bin/env bash
# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

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
