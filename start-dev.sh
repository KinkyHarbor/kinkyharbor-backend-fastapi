#!/usr/bin/env bash

echo -e "\nStart docker services ..."
docker-compose -f docker-compose.dev.yml up -d --build

echo -e "\nActivate Python env ..."
source env/bin/activate

echo -e "\nInstall requirements"
pip install -r requirements.txt

echo -e "\nStart uvicorn dev server ..."
DEBUG=True \
uvicorn harbor.app:app \
--reload \
--host=localhost \
--log-level=info