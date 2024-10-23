#!/bin/bash

# Add config/creds copying here..
aws s3 cp s3://$S3_CONFIG_BUCKET/$S3_CONFIG_PATH/env.config /app/.env

# Change to the application directory
cd /app

# Start the Uvicorn server
uvicorn main:app --host 0.0.0.0 --port 3000
