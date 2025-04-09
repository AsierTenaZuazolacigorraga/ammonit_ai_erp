#! /usr/bin/env bash

# Change to root
cd "$(dirname "$0")"
cd ..

source .env

# Bring the .env to: aws
scp -i ${AWS_KEY_PATH} .env ${AWS_USER}@${AWS_HOST}:${AWS_CLONED_IN}/
scp -i ${AWS_KEY_PATH} ./frontend/.env ${AWS_USER}@${AWS_HOST}:${AWS_CLONED_IN}/frontend/
scp -i ${AWS_KEY_PATH} -r ./backend/.gitignores/azure_tokens ${AWS_USER}@${AWS_HOST}:${AWS_CLONED_IN}/backend/.gitignores/

# Some adjustments   
ssh -i "${AWS_KEY_PATH}" -t "${AWS_USER}@${AWS_HOST}" << EOF
    cd ${AWS_CLONED_IN}
    sed -i -e 's/^ENVIRONMENT=.*$/ENVIRONMENT=production/' -e 's/^DOMAIN=.*$/DOMAIN=ammonit.es/' .env
EOF
