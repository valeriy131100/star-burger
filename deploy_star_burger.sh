#!/bin/bash
set -e

export $(xargs < .env)

echo Updating code
git pull

echo Installing librarires
venv/bin/python -m pip install -r requirements.txt
npm ci
sudo apt install libpq-dev python3-dev
echo Building things
parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
venv/bin/python manage.py collectstatic --noinput

echo Applying migrations
venv/bin/python manage.py migrate --noinput

echo Restarting services
systemctl restart starburger
systemctl reload nginx

echo Reporting Rollbar
http POST https://api.rollbar.com/api/1/deploy X-Rollbar-Access-Token:$ROLLBAR_TOKEN environment=$ROLLBAR_ENVIRONMENT revision=$(git rev-parse HEAD)

echo Deployed successfully
