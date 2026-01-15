# select base image
FROM python:3.14-slim

# install server dependencies
RUN apt-get update && apt-get install -y \
    curl \
    openssh-client \
    git \
    && rm -rf /var/lib/apt/lists/*

