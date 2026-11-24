#!/usr/bin/env bash
set -Eeuo pipefail

# Official postgres entrypoint runs this script only for a new, empty volume.
# psql variables ensure the password is SQL-escaped rather than interpolated.
psql -v ON_ERROR_STOP=1 \
  -v "app_password=${APP_DB_PASSWORD:?APP_DB_PASSWORD must be set}" \
  --username "${POSTGRES_USER}" --dbname postgres <<'SQL'
SELECT format('CREATE ROLE docuentityseek_app LOGIN PASSWORD %L', :'app_password')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'docuentityseek_app')
\gexec

SELECT 'CREATE DATABASE docuentityseek OWNER docuentityseek_app'
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'docuentityseek')
\gexec
SQL

# Ensure tables are created by the application role, not by postgres.
psql -v ON_ERROR_STOP=1 \
  --username "${POSTGRES_USER}" --dbname docuentityseek <<'SQL'
SET ROLE docuentityseek_app;
\i /docker-init/01_schema.sql
\i /docker-init/02_seed.sql
SQL
