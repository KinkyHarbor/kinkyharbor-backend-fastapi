#!/usr/bin/env bash

echo -e "\nStart docker services ..."
docker-compose -f docker-compose.dev.yml up -d

echo -e "\nActivate Python env ..."
source env/bin/activate

echo -e "\nOpen sub shell ..."
/usr/bin/env bash -c '
echo -e "\nChange to app directory ..."
cd app

echo -e "\nStart uvicorn dev server ..."
FRONTEND_URL=http://192.168.20.50:3000 \
EMAIL_FROM_ADDRESS=no-reply@kinkyharbor.com \
EMAIL_SECURITY=unsecure \
uvicorn harbor.app:app \
--reload \
--host=0.0.0.0
'