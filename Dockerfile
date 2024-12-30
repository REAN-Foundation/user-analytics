# Build stage
FROM alpine:3.21 AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /build

# Install build dependencies and update zlib to a non-vulnerable version
RUN apk update && apk add --no-cache \
    build-base \
    python3 \
    python3-dev \
    py3-pip \
    bash \
    pkgconfig \
    mariadb-dev \
    zlib-dev \
    && rm -rf /var/cache/apk/*

# Create and activate a virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM alpine:3.21

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Install runtime dependencies and update zlib to a non-vulnerable version
RUN apk update && apk add --no-cache \
    python3 \
    bash \
    pandoc \
    texlive \
    texlive-xetex \
    fontconfig \
    libmagic \
    mariadb-client \
    zlib-dev \
    && rm -rf /var/cache/apk/*

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY  . .

# Ensure the entrypoint script is executable
RUN chmod +x /app/entrypoint.sh

# Expose the application port
EXPOSE 3000

# Set the entrypoint
ENTRYPOINT ["/bin/bash", "-c", "/app/entrypoint.sh"]
