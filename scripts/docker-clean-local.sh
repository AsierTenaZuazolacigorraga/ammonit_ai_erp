#! /usr/bin/env bash

# Change to root
cd "$(dirname "$0")"
cd ..

source .env

# Add hosts
sudo sh -c 'echo "127.0.0.1 dashboard.localhost.tiangolo.com" >> /etc/hosts'
sudo sh -c 'echo "127.0.0.1 api.localhost.tiangolo.com" >> /etc/hosts'

# Up docker
docker compose -f docker-compose.traefik.yml up -d --build
docker compose -f docker-compose.yml up -d --build