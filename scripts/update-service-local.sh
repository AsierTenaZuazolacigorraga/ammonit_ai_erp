#! /usr/bin/env bash

# Change to root
cd "$(dirname "$0")"
cd ..

source .env

sh ./scripts/docker-clean-local.sh