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

# Configure environment
python3 manage.py makemigrations movies
python3 manage.py migrate

# Configuration Model Weights
mkdir -p cache
python3 manage.py load_model_weights