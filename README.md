# game-help-builder
Game Help Builder

## Installation
- Install Docker
https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04

- Install Docker Compose
https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-20-04

- Install haveged
https://www.digitalocean.com/community/tutorials/how-to-setup-additional-entropy-for-cloud-servers-using-haveged

- Upload the web application files

- Switch to the uploaded web application folder

- Create new file called ".env" with content similar to:
```
DATABASE_NAME=gamehelpparser
DATABASE_URL=postgres://postgres:postgres@db:5432/gamehelpparser
PORT=80
SERVERNAMES=45.35.94.235 help.aelisus.com
DEBUG=False
```
- Make sure the _SERVERNAMES_ matches server IP and/or Domains that will load the web application

- If free SSL is needed, follow the next couple of steps:

 - Make sure the SSL generator script is executable:
```
chmod +x ./getsslcert.sh
```

 - Run SSL generator script with domain that will load the web application:
```
./getsslcert.sh help.aelisus.com
```

- Start the web application by running:
```
docker compose up -d
```

- Create Database tables:
```
docker compose exec web python manage.py migrate
```

- Create Admin account:
```
docker compose exec web python manage.py createsuperuser
```
