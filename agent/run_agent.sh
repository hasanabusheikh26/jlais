#!/bin/bash

# Set SSL certificate path
export SSL_CERT_FILE=$(.venv/bin/python -m certifi)
export REQUESTS_CA_BUNDLE=$SSL_CERT_FILE

# Activate virtual environment
source .venv/bin/activate

# Run the agent
python main.py dev
