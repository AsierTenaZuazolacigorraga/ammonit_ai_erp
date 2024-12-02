#!/bin/bash

# Define paths
current_path=$(dirname "$0")
cd $current_path
cd ..
root_path=$(pwd)

# Locate, activate, path, and run
source .venv/bin/activate
export PYTHONPATH=$PYTHONPATH:$root_path
python publisher/src/__main__.py
deactivate