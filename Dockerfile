# Use Alpine base image for building
FROM alpine:3.18 AS builder

# Set the working directory
WORKDIR /app

# Install necessary system dependencies
RUN apk update && apk add --no-cache \
    bash \
    pandoc \
    libmagic \
    fontconfig \
    build-base \
    openssl \
    && apk upgrade openssl \
    && rm -rf /var/cache/apk/*

# Add application code to /app
ADD . /app

RUN chmod +x /app/entrypoint.sh

# Expose the application port
EXPOSE 3000

ENTRYPOINT ["/bin/bash", "-c", "/app/entrypoint.sh"]
