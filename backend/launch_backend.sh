#!/bin/bash

# Define paths
current_path=$(dirname "$0")
cd $current_path
cd ..
root_path=$(pwd)

# Locate, activate, path, and run
source .venv/bin/activate
export PYTHONPATH=$PYTHONPATH:$root_path
uvicorn src.__main__:app --reload --host 0.0.0.0 --port 8000 --app-dir backend 
deactivate