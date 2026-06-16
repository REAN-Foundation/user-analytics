# Use Python 3.12 Alpine; psycopg2 currently fails to build on Python 3.13 in this stack.
FROM python:3.12-alpine

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
    mariadb-dev \
    postgresql-dev \
    aws-cli && \
    python3 -m ensurepip --upgrade && \
    pip install --no-cache-dir --upgrade pip
    # pip install awscli


WORKDIR /app

# Layer 1: dependencies (cached unless requirements.txt changes)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Layer 2: entrypoint (cached unless entrypoint.sh changes)
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Layer 3: app code (only this layer re-uploads on code changes)
COPY . /app/

# Expose the application port
EXPOSE 3000

# Use a command to keep the container running or start the app
ENTRYPOINT ["/bin/bash", "-c", "/app/entrypoint.sh"]
