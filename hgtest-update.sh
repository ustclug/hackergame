#!/usr/bin/env bash

set -x

cd /opt/hackergame2021-challenges
git pull

cd /opt/hgtest
git pull
source .venv/bin/activate
export DJANGO_SETTINGS_MODULE=conf.settings.hgtest
pip install -r requirements.txt
./manage.py migrate
./manage.py collectstatic --noinput
./manage.py import_data /opt/hackergame2021-challenges
deactivate

cp /opt/hgtest/conf/nginx-sites/hgtest /etc/nginx/sites-available/hgtest
cp /opt/hgtest/conf/uwsgi-apps/hgtest.ini /etc/uwsgi/apps-available/hgtest.ini

service uwsgi reload
service nginx reload
