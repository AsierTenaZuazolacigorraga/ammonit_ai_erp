#! /usr/bin/env bash

# Change to root
cd "$(dirname "$0")"
cd ..

source .env

sh ./scripts/update-secret-files.sh

ssh -i "${AWS_KEY_PATH}" -t "${AWS_USER}@${AWS_HOST}" << EOF
    cd ${AWS_CLONED_IN}
    git remote set-url origin ${GIT_URL}   # Update remote URL with token
    git pull                               # Pull the latest changes from the repository
    ./scripts/docker-clean.sh
EOF
