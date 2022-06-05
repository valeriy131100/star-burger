#!/bin/bash

/usr/local/bin/docker-compose -f /opt/star-burger/docker-compose.prod.yml run --no-deps certbot renew --webroot --webroot-path=/var/www/html \
&& /usr/local/bin/docker-compose -f /opt/star-burger/docker-compose.prod.yml kill -s SIGHUP nginx
