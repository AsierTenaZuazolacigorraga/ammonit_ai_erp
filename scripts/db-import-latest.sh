#! /usr/bin/env bash

# Change to root
cd "$(dirname "$0")"
cd ..

# Import db
cd db_backup

# Backup db
latest_backup=latest_backup.tar.gz
volume_name=iot_bind_app-db-data
docker run --rm -v $volume_name:/volume -v $(pwd):/backup busybox tar xzf /backup/$latest_backup -C /volume .
