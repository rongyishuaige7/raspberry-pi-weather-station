#!/usr/bin/env bash
set -euo pipefail

: "${MYSQL_HOST:=127.0.0.1}"
: "${MYSQL_PORT:=3306}"
: "${MYSQL_DATABASE:=weather_station}"
: "${MYSQL_USER:=test_weather_user}"
: "${MYSQL_PASSWORD:=replace_with_ci_database_password}"
: "${MYSQL_ROOT_PASSWORD:=replace_with_ci_root_password}"
: "${JWT_SECRET:=replace_with_ci_jwt_secret_at_least_32_characters}"
export MYSQL_HOST MYSQL_PORT MYSQL_DATABASE MYSQL_USER MYSQL_PASSWORD MYSQL_ROOT_PASSWORD JWT_SECRET
export USE_MOCK_SENSORS=1
export RUN_MYSQL_INTEGRATION=1

python3 -m unittest discover -s tests -p 'test_mysql_integration.py' -v
