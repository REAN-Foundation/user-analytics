FROM python:3.10
ADD . /app

# Install dependencies including pandoc and AWS CLI
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    pandoc \
    libexpat1 \
    texlive-xetex \
    texlive-fonts-recommended \
    texlive-plain-generic \
    texlive-latex-extra \
    python3 \
    python3-pip \
    && pip3 install --upgrade pip \
    && pip3 install awscli \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN python -m venv venv
RUN . venv/bin/activate
RUN pip install --upgrade pip
RUN pip install setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Make sure entrypoint.sh is executable
RUN chmod +x /app/entrypoint.sh

EXPOSE 3000

# Set the entrypoint
ENTRYPOINT ["/bin/bash", "-c", "/app/entrypoint.sh"]
