#!/bin/sh
python manage.py migrate
python manage.py collectstatic --noinput
if [ -f "privkey.pem" ] && [ -f "cert.pem" ]
then
    gunicorn game_help_parser.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --worker-class=gevent \
    --worker-connections=1000 \
    --workers=8 \
    --timeout $GUNICORN_TIMEOUT \
    --keyfile privkey.pem --certfile cert.pem
else
    gunicorn game_help_parser.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --timeout $GUNICORN_TIMEOUT
fi
