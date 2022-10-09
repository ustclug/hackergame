#!/bin/sh

NAME=hg

cd "$(dirname "$0")"
docker rm -f "$NAME"
docker run --name="$NAME" --hostname="$NAME" -itd \
  -e DJANGO_SETTINGS_MODULE=conf.settings.hackergame \
  -v "$PWD"/conf/local_settings.py:/opt/hackergame/conf/local_settings.py:ro \
  -v /run/uwsgi/app/hackergame/:/run/uwsgi/app/hackergame/:rw \
  -v /var/opt/hackergame/:/var/opt/hackergame/:rw \
  -v /var/run/postgresql/:/var/run/postgresql/:rw \
  hg:latest
