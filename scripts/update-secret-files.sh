#!/bin/bash

source .env

# Bring the .env to: aws
scp -i ${AWS_KEY_PATH} .env ${AWS_USER}@${AWS_HOST}:${AWS_CLONED_IN}/
scp -i ${AWS_KEY_PATH} ./frontend/.env ${AWS_USER}@${AWS_HOST}:${AWS_CLONED_IN}/frontend/
scp -i ${AWS_KEY_PATH} -r ./backend/.gitignores/azure_tokens ${AWS_USER}@${AWS_HOST}:${AWS_CLONED_IN}/backend/.gitignores/

