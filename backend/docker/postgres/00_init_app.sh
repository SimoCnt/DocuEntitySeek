#!/usr/bin/env bash

set -euo pipefail

echo "Creating DocuEntitySeek application role..."

if ! psql --username "$POSTGRES_USER" --dbname postgres --tuples-only \
    --command "SELECT 1 FROM pg_roles WHERE rolname = 'docuentityseek_app';" | grep -q 1
then
    psql --username "$POSTGRES_USER" --dbname postgres \
        --set=app_password="$APP_DB_PASSWORD" --set=ON_ERROR_STOP=1 <<'EOSQL'

CREATE ROLE docuentityseek_app
WITH LOGIN
PASSWORD :'app_password'
NOSUPERUSER
NOCREATEDB
NOCREATEROLE;

EOSQL
fi

echo "Creating DocuEntitySeek database..."

if ! psql --username "$POSTGRES_USER" --dbname postgres --tuples-only \
    --command "SELECT 1 FROM pg_database WHERE datname = 'docuentityseek';" | grep -q 1
then
    psql --username "$POSTGRES_USER" --dbname postgres \
        --set=ON_ERROR_STOP=1 \
        --command "CREATE DATABASE docuentityseek OWNER docuentityseek_app ENCODING 'UTF8';"
fi

psql --username "$POSTGRES_USER" --dbname postgres \
    --set=ON_ERROR_STOP=1 \
    --command "ALTER DATABASE docuentityseek SET timezone TO 'UTC';"

echo "Creating relational schema..."

PGPASSWORD="$APP_DB_PASSWORD" psql \
    --username docuentityseek_app \
    --dbname docuentityseek \
    --set=ON_ERROR_STOP=1 \
    --file /docker-init/01_schema.sql

echo "Loading initial application data..."

PGPASSWORD="$APP_DB_PASSWORD" psql \
    --username docuentityseek_app \
    --dbname docuentityseek \
    --set=ON_ERROR_STOP=1 \
    --file /docker-init/02_seed.sql

echo "DocuEntitySeek database initialized."