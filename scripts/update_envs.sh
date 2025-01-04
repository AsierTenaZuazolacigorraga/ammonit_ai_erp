#!/bin/bash

source .env

# Bring the .env to: pi
scp .env ${DEVICE_USER}@${DEVICE_HOST}:${DEVICE_CLONED_IN}/

# Bring the .env to: aws
scp -i ${AWS_KEY_PATH} .env ${AWS_USER}@${AWS_HOST}:${AWS_CLONED_IN}/
scp -i ${AWS_KEY_PATH} ./frontend/.env ${AWS_USER}@${AWS_HOST}:${AWS_CLONED_IN}/frontend/

# This is not needed now, as mqtt works without tls
# scp -i ${KEY_PATH} ./broker/config/custom_ca.crt ${USER}@${HOST}:${CLONED_IN}/broker/config/
# scp -i ${KEY_PATH} ./broker/config/custom_server.crt ${USER}@${HOST}:${CLONED_IN}/broker/config/
# scp -i ${KEY_PATH} ./broker/config/custom_server.key ${USER}@${HOST}:${CLONED_IN}/broker/config/
# scp -i ${KEY_PATH} ./broker/config/custom.pwfile ${USER}@${HOST}:${CLONED_IN}/broker/config/