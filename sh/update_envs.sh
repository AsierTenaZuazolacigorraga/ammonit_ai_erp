#!/bin/bash

source .env

# Bring the .env files to remote
scp -i ${KEY_PATH} .env ${USER}@${HOST}:${CLONED_IN}/
scp -i ${KEY_PATH} ./app/.env ${USER}@${HOST}:${CLONED_IN}/app/