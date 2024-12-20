#!/bin/bash

source .env

sh ./update_envs.sh

# Use the loaded variables
ssh -i "$KEY_PATH" -t "$USER@$HOST" << EOF
    cd $CLONED_IN
    git remote set-url origin $GIT_URL   # Update remote URL with token
    git pull                             # Pull the latest changes from the repository
    docker-compose down                  # Stop existing Docker containers

    #docker container prune -f         # Remove stopped containers
    #docker image prune -a -f          # Remove all unused images
    #docker volume prune -f            # Remove unused volumes
    #docker network prune -f           # Remove unused networks
    #docker system prune -a --volumes -f  # Full cleanup (includes volumes)

    docker-compose up --build            # Build and start Docker containers
EOF