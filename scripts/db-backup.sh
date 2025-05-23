#! /usr/bin/env bash

# Change to root
cd "$(dirname "$0")"
cd ..

# Create db_backup directory if it doesn't exist
mkdir -p db_backup
cd db_backup

# Backup db
date_backup=$(date +%Y%m%d_%H%M%S)_backup.tar.gz
latest_backup=latest_backup.tar.gz
volume_name=iot_bind_app-db-data
docker run --rm -v $volume_name:/volume -v $(pwd):/backup busybox tar czf /backup/$date_backup -C /volume .
cp $date_backup $latest_backup
