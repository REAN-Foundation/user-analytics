#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Function to handle errors
handle_error() {
    echo "Error on line $1"
    exit 1
}

# Trap errors and call the error handler
trap 'handle_error $LINENO' ERR

# Add config/creds copying here..
if ! aws s3 cp s3://$S3_CONFIG_BUCKET/$S3_CONFIG_PATH/env.config /app/.env; then
    echo "Failed to copy env.config from S3."
    exit 1
fi

# Change to the application directory
cd /app

# Start the Uvicorn server
if ! uvicorn main:app --host 0.0.0.0 --port 3000; then
    echo "Failed to start Uvicorn server."
    exit 1
fi
