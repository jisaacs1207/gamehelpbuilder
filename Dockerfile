# pull official base image
FROM python:3.8.9-alpine3.13

RUN pip install --upgrade pip

# install psycopg2
RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql-dev \
    && pip install psycopg2

# set work directory
WORKDIR /app

# install dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG False
ENV SERVERNAMES dev.box gamehelpbuilder.herokuapp.com
# ENV GUNICORN_NUM_WORKERS 3
ENV GUNICORN_TIMEOUT 240

# collect static files
RUN python manage.py collectstatic --noinput

# add and run as non-root user
RUN adduser -D myuser
USER myuser

ENTRYPOINT ["/app/start.sh"]
