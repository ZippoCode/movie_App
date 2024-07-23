#!/bin/bash

ENV_NAME=".venv"

# Create the virtual environment (overwrite if it exists)
python3 -m venv $ENV_NAME
echo "Virtual environment $ENV_NAME created."
source $ENV_NAME/bin/activate
echo "Virtual environment $ENV_NAME activated."

# Install the necessary packages
pip install -r requirements.txt
echo "Packages installed from requirements.txt."