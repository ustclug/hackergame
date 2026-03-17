#!/bin/sh -e

# Set permission for /run/uwsgi/app/hackergame-docker/
mkdir -p /run/uwsgi/app/hackergame-docker/
chown www-data:www-data /run/uwsgi/app/hackergame-docker/

echo "Note that /opt/hackergame/ shall be readable by uwsgi (www-data in container)."
echo "You could set it to be readable by everyone: chmod -R a+rX hackergame/"

echo "If this is your first time to run this container, you should run:"
echo " docker exec -it hackergame ./manage.py migrate"
echo " docker exec -it hackergame ./manage.py collectstatic"

# Start uwsgi
exec /usr/local/bin/uwsgi --master --ini conf/uwsgi.ini \
    --ini conf/uwsgi-apps/hackergame-docker.ini \
    --set-placeholder appname=hackergame-docker
