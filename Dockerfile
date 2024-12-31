# Build stage
FROM python:3.10-slim-bookworm AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Set the working directory
WORKDIR /build

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    python3-venv \
    libmariadb-dev \
    pkg-config \
    curl \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt . 
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.10-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PATH="/opt/venv/bin:$PATH"

# Set the working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    pandoc \
    texlive-xetex \
    texlive-fonts-recommended \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-plain-generic \
    fontconfig \
    libmagic1 \
    bash \
    curl \
    mariadb-client \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/* /usr/share/doc/* /usr/share/man/*

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Create a non-root user
RUN useradd -r -s /bin/bash appuser && \
    mkdir -p /app /home/appuser && \
    chown -R appuser:appuser /app /home/appuser

# Copy application code
COPY --chown=appuser:appuser . .

# Ensure the entrypoint script is executable
RUN chmod +x /app/entrypoint.sh

# Set permissions
RUN chmod -R 755 /app && \
    chmod -R 700 /home/appuser

# Switch to the non-root user
USER appuser

# Add health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Expose the application port
EXPOSE 3000

# Set the entrypoint
ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]
