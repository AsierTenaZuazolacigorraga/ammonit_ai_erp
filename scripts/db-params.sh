#! /usr/bin/env bash

export backup_dir=db_backup
export date_backup=$(date +%Y%m%d_%H%M%S)_backup.tar.gz
export latest_backup=latest_backup.tar.gz
export volume_name=iot_bind_app-db-data