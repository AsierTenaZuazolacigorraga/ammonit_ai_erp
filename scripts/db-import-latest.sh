#! /usr/bin/env bash

# Change to root
cd "$(dirname "$0")"
cd ..

# Load params
sh ./scripts/db-params.sh

# Import db
cd $backup_dir

# Import db
docker run --rm -v $volume_name:/volume -v $(pwd):/backup busybox tar xzf /backup/$latest_backup -C /volume .
