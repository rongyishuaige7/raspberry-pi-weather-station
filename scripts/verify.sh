#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export MYSQL_USER="verify_weather"
export MYSQL_PASSWORD="replace_with_verify_database_password"
export JWT_SECRET="replace_with_verify_jwt_secret_at_least_32_characters"

cleanup() {
  rm -rf raspi/__pycache__ raspi/api/__pycache__ raspi/collector/__pycache__ \
    tests/__pycache__ upper/WeatherStation/bin upper/WeatherStation/obj
}
trap cleanup EXIT
cleanup

python3 scripts/secret_scan.py
python3 scripts/check_repo.py
python3 -m compileall -q raspi tests
python3 -m unittest discover -s tests -p 'test_source_contracts.py' -v

dotnet restore upper/WeatherStation.sln --locked-mode
dotnet build upper/WeatherStation.sln --configuration Release --no-restore
