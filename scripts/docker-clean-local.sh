#! /usr/bin/env bash

# Change to root
cd "$(dirname "$0")"
cd ..

source .env

# Stop docker
docker compose down

# Remove all docker info
if [ "$(docker ps -aq)" ]; then
    docker stop $(docker ps -aq)
fi
docker rm $(docker ps -aq)
docker rmi $(docker images -q) 
# docker volume rm $(docker volume ls -q) 
# docker network rm $(docker network ls -q) 
docker builder prune --all --force

# Up docker
docker compose up -d --build
