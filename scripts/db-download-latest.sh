#! /usr/bin/env bash

# Change to root
cd "$(dirname "$0")"
cd ..

source .env

# Backup local db
bash ./scripts/db-backup.sh

# Backup remote db
ssh -i "${AWS_KEY_PATH}" -t "${AWS_USER}@${AWS_HOST}" << EOF
    cd ${AWS_CLONED_IN}
    bash ./scripts/db-backup.sh
EOF

# Download db
scp -i ${AWS_KEY_PATH} ${AWS_USER}@${AWS_HOST}:${AWS_CLONED_IN}/db_backup/latest_backup.tar.gz ./db_backup/latest_backup.tar.gz

# Import db
bash ./scripts/db-import-latest.sh