#!/bin/bash

source .env

# Bring the .env files to remote
scp -i ${KEY_PATH} .env ${USER}@${HOST}:${CLONED_IN}/
scp -i ${KEY_PATH} ./app/.env ${USER}@${HOST}:${CLONED_IN}/app/
scp -i ${KEY_PATH} ./broker/config/custom_ca.crt ${USER}@${HOST}:${CLONED_IN}/broker/config/
scp -i ${KEY_PATH} ./broker/config/custom_server.crt ${USER}@${HOST}:${CLONED_IN}/broker/config/
scp -i ${KEY_PATH} ./broker/config/custom_server.key ${USER}@${HOST}:${CLONED_IN}/broker/config/
scp -i ${KEY_PATH} ./broker/config/custom.pwfile ${USER}@${HOST}:${CLONED_IN}/broker/config/