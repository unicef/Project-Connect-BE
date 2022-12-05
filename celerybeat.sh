#!/usr/bin/env bash
set -ex

# export environment variables to make them available in ssh session
for var in $(compgen -e); do
    echo "export $var=${!var}" >> /etc/profile
done

echo "Starting SSH ..."
service ssh start

export FLASK_APP=hello.py
pipenv run python -m flask run --host 0.0.0.0 --port 8000 &

pipenv run celery -A proco.taskapp beat $*
