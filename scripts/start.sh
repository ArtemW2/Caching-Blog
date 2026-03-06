#!/bin/bash
set -e

echo "Waiting for PostgreSQL to be ready..."
while ! nc -z postgres 5432; do   
  sleep 1
done
echo "PostgreSQL is ready"

echo "Waiting for Redis to be ready..."
while ! nc -z redis 6379; do
  sleep 1
done
echo "Redis is ready"

echo "Running database migrations..."
uv run alembic upgrade head

echo "Starting application..."
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload