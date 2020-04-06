#!/usr/bin/env bash

echo -e "\nStart docker services ..."
docker-compose -f docker-compose.dev.yml up -d

echo -e "\nActivate Python env ..."
source env/bin/activate

echo -e "\nInstall requirements"
pip install -r requirements.txt

echo -e "\nStart uvicorn dev server ..."
FRONTEND_URL=http://localhost:3000 \
EMAIL_FROM_ADDRESS=no-reply@kinkyharbor.com \
EMAIL_SECURITY=unsecure \
uvicorn harbor.app:app \
--reload \
--host=localhost \
--log-level=info