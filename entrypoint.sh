#!/bin/bash
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Seeding database with test data..."
python seed.py

exec "$@"