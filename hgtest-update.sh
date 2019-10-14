#!/usr/bin/env bash

set -x

cd /opt/hackergame2019-problems
GIT_SSH_COMMAND='ssh -i /root/.ssh/hackergame2019-problems.key' git pull

cd /opt/hgtest
git pull
source .venv/bin/activate
export DJANGO_SETTINGS_MODULE=conf.settings.hgtest
pip install -r requirements.txt
./manage.py migrate
./manage.py collectstatic --noinput
./manage.py import_data /opt/hackergame2019-problems
deactivate

service uwsgi reload
service nginx reload
