DATA=/data

mkdir -p $DATA/static $DATA/media $DATA/log

if [ ! -f "$DATA/secret.key" ]; then
    echo $(cat /dev/urandom | head -2 | sha512sum | head -c 64) > "$DATA/secret.key"
fi

export DJANGO_SETTINGS_MODULE='backend.production_test'

while ! python manage.py init_dev -U 300 -S 2000; do
  echo "psql not ready, sleeping..."
  sleep 0.5
done
python manage.py collectstatic --noinput

gunicorn backend.wsgi:application --bind 0.0.0.0:8000
