# Use the latest stable Python 3.10 and Alpine image
FROM python:3.10-alpine3.19

# Set environment variables to avoid writing bytecode and unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies and upgrade vulnerable packages
RUN apk update && \
    apk upgrade && \
    apk add --no-cache \
    pandoc \
    texlive-xetex \
    bash \
    build-base \
    mariadb-dev && \
    python3 -m ensurepip --upgrade && \
    pip install --no-cache-dir --upgrade pip && \
    pip install awscli

# Set the working directory for the application
WORKDIR /app

# Copy requirements file first to install dependencies separately
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . /app/

# Ensure that entrypoint.sh has executable permissions
RUN chmod +x /app/entrypoint.sh

# Expose the application port
EXPOSE 3000

# Use a command to keep the container running or start the app
ENTRYPOINT ["/bin/bash", "-c", "/app/entrypoint.sh"]
