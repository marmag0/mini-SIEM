# select base image
FROM python:3.14-slim

# install server dependencies
RUN apt-get update && apt-get install -y \
    curl \
    openssh-client \
    git \
    && rm -rf /var/lib/apt/lists/*

# cloudflare installation
RUN ARCH=$(dpkg --print-architecture) && \
    echo "Server's architecture: ${ARCH}" && \
    curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-${ARCH}.deb && \
    dpkg -i cloudflared.deb && \
    rm cloudflared.deb

# set working directory
WORKDIR /app

# install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src
ENV FLASK_APP=src/app.py
ENV FLASK_RUN_HOST=0.0.0.0
CMD ["flask", "run", "--debug"]

