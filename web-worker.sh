#!/usr/bin/env bash
set -ex

# export environment variables to make them available in ssh session
for var in $(compgen -e); do
    echo "export $var=${!var}" >> /etc/profile
done

eval $(printenv | awk -F= '{print "export " "\""$1"\"""=""\""$2"\"" }' >> /etc/profile)

echo "Starting SSH ..."
service ssh start

pipenv run python manage.py migrate
pipenv run python manage.py collectstatic --noinput
pipenv run gunicorn config.wsgi:application -b 0.0.0.0:8000 -w 8 --timeout=60
