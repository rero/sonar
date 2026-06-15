#!/usr/bin/env bash
# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE ROLE sonar WITH LOGIN PASSWORD 'sonar';
    ALTER ROLE sonar CREATEDB;
    \du;
EOSQL
