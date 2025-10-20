#!/bin/bash
set -e

# Запускаем миграции перед запуском любой команды
echo "Running database migrations..."
alembic upgrade head

# Выполняем переданную команду
exec "$@"