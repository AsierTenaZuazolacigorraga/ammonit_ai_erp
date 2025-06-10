#! /usr/bin/env bash

# Change to root
cd "$(dirname "$0")"
cd ..

# Load params
source ./scripts/db-params.sh

# Import db
cd $backup_dir

# Import db
# docker run --rm -v $volume_name:/volume -v $(pwd):/backup busybox:1.35.0 tar xzf /backup/$latest_backup -C /volume .
echo "Import database from $latest_backup manually by now ..."