#! /usr/bin/env bash

backup_dir=db_backup
date_backup=$(date +%Y%m%d_%H%M%S)_backup.tar.gz
latest_backup=latest_backup.tar.gz
volume_name=iot_bind_app-db-data