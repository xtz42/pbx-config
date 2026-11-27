#!/usr/bin/env bash
# Применяет собственные миграции db/migrations/NNNN_*.up.sql к базе тенанта.
#   db/migrate.sh <база> [роль-владелец]
# Запускается от пользователя postgres (локальный сокет). Каждая миграция —
# в отдельной транзакции, применённые записываются в pbx_schema_migrations.
# Откат — вручную файлом NNNN_*.down.sql и удалением строки из pbx_schema_migrations.
set -euo pipefail

DB="${1:?укажите базу}"
OWNER="${2:-${DB}_owner}"
DIR="$(cd "$(dirname "$0")" && pwd)/migrations"
export PGOPTIONS="-c client_min_messages=warning"
PSQL=(psql -X -q -v ON_ERROR_STOP=1 -d "${DB}")

"${PSQL[@]}" -c "SET ROLE ${OWNER}; CREATE TABLE IF NOT EXISTS pbx_schema_migrations (
    version varchar(64) PRIMARY KEY, applied_at timestamptz NOT NULL DEFAULT now())"

applied=0
for f in "${DIR}"/[0-9][0-9][0-9][0-9]_*.up.sql; do
  [ -e "$f" ] || continue
  ver="$(basename "$f" .up.sql)"
  if "${PSQL[@]}" -Atc "SELECT 1 FROM pbx_schema_migrations WHERE version = '${ver}'" | grep -q 1; then
    continue
  fi
  echo ">>> ${DB}: ${ver}"
  "${PSQL[@]}" -1 -c "SET ROLE ${OWNER}" -f "$f" -c "INSERT INTO pbx_schema_migrations (version) VALUES ('${ver}')"
  applied=$((applied + 1))
done
echo "applied=${applied}"
