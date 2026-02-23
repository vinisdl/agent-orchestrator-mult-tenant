#!/bin/sh
set -e
if [ "$WAIT_FOR_DB" = "true" ] || [ "$WAIT_FOR_DB" = "True" ]; then
  python /app/scripts/wait_for_db.py
fi
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 "$@"
