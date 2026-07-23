#!/usr/bin/env bash
# Comando de inicio para Azure App Service (Linux).
# Configúralo en: App Service > Configuración > Comando de inicio:
#   startup.sh
# O pega directamente la línea de gunicorn de más abajo.

set -e

# Aplica migraciones y recopila estáticos en cada arranque.
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Levanta la app. Azure expone el puerto en $PORT.
gunicorn config.wsgi:application \
    --bind=0.0.0.0:${PORT:-8000} \
    --timeout 600 \
    --workers 2
