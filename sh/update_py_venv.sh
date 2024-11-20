#!/bin/bash

# Define the virtual environment directory name
VENV_DIR=".venv"

# Check if the virtual environment directory already exists
if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists."
else
    echo "Virtual environment does not exist. Creating one..."

    # Create a virtual environment using Python 3
    sudo apt install python3-pip
    sudo apt install python3-venv
    python3 -m venv $VENV_DIR

    # Check if the virtual environment was successfully created
    if [ $? -eq 0 ]; then
        echo "Virtual environment created successfully."
    else
        echo "Failed to create virtual environment."
        exit 1
    fi
fi

# Activate the virtual environment
echo "Activating the virtual environment..."
source $VENV_DIR/bin/activate

# Check if the virtual environment was successfully activated
if [ $? -eq 0 ]; then
    echo "Virtual environment activated."
    pip install -r requirements.txt
else
    echo "Failed to activate the virtual environment."
    exit 1
fi
