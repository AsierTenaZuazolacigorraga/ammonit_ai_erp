#! /usr/bin/env bash

# Change to root
cd "$(dirname "$0")"
cd ..

# Load params
sh ./scripts/db-params.sh

# Create db_backup directory if it doesn't exist
mkdir -p $backup_dir
cd $backup_dir

# Backup db
docker run --rm -v $volume_name:/volume -v $(pwd):/backup busybox:1.35.0 tar czf /backup/$date_backup -C /volume .
cp $date_backup $latest_backup
