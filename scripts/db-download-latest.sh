#! /usr/bin/env bash

# Change to root
cd "$(dirname "$0")"
cd ..

source .env

# Backup local db
sh ./scripts/db-backup.sh

# Backup remote db
ssh -i "${AWS_KEY_PATH}" -t "${AWS_USER}@${AWS_HOST}" << EOF
    sh ./scripts/db-backup.sh
EOF

# Download db
scp -i ${AWS_KEY_PATH} ${AWS_USER}@${AWS_HOST}:${AWS_CLONED_IN}/db_backup/latest_backup.tar.gz ./db_backup/latest_backup.tar.gz

# Import db
sh ./scripts/db-import-latest.sh