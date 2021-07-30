#!/bin/sh
docker run -it --rm --name certbot -v "/etc/letsencrypt:/etc/letsencrypt" -v "/var/lib/letsencrypt:/var/lib/letsencrypt" -p 80:80 -p 443:443 certbot/certbot certonly --standalone --agree-tos -d "$1"
cp "/etc/letsencrypt/live/$1/cert.pem" .
cp "/etc/letsencrypt/live/$1/privkey.pem" .
chmod 0644 *.pem