#! /usr/bin/env bash

# Change to root
cd "$(dirname "$0")"
cd ..

source .env
source ./scripts/db-params.sh

# Backup local db
bash ./scripts/db-backup.sh

# Backup remote db
ssh -i "${AWS_KEY_PATH}" -t "${AWS_USER}@${AWS_HOST}" << EOF
    cd ${AWS_CLONED_IN}
    bash ./scripts/db-backup.sh
EOF

# Download db
scp -i ${AWS_KEY_PATH} ${AWS_USER}@${AWS_HOST}:${AWS_CLONED_IN}/${backup_dir}/${latest_backup} $(pwd)/${backup_dir}/${latest_backup}

# Backup remote db
ssh -i "${AWS_KEY_PATH}" -t "${AWS_USER}@${AWS_HOST}" << EOF
    cd ${AWS_CLONED_IN}
    rm -rf ${backup_dir}
EOF

# Import db
bash ./scripts/db-import-latest.sh