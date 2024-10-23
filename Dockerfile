FROM python:3.10

# Install dependencies including pandoc
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    pandoc \
    libexpat1 \
    texlive-xetex \
    texlive-fonts-recommended \
    texlive-plain-generic \
    texlive-latex-extra \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN python -m venv venv
RUN . venv/bin/activate
RUN pip install --upgrade pip
RUN pip install setuptools wheel
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app

# Make sure entrypoint.sh is executable
RUN chmod +x /app/entrypoint.sh

EXPOSE 3000

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
