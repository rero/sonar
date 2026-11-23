#!/usr/bin/env bash
# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

# Verify that all services are running before continuing
check_ready() {
    RETRIES=20
    while ! $2
    do
        echo "Waiting for $1, $((RETRIES--)) remaining attempts..."
        sleep 2
        if [ $RETRIES -eq 0 ]
        then
            echo "Couldn't reach $1"
            exit 1
        fi
    done
}
_db_check(){ docker compose exec --user postgres db bash -c "pg_isready" &>/dev/null; }
check_ready "Postgres" _db_check

_os_check(){ curl --output /dev/null --silent --head --fail http://localhost:9200 &>/dev/null; }
check_ready "OpenSearch" _os_check

_redis_check(){ docker compose exec cache bash -c 'redis-cli ping' | grep 'PONG' &> /dev/null; }
check_ready "Redis" _redis_check

_rabbit_check(){ docker compose exec mq bash -c "rabbitmqctl status" &>/dev/null; }
check_ready "RabbitMQ" _rabbit_check
