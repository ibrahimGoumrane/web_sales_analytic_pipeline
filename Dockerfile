# Custom Airflow image with plotting libraries
FROM apache/airflow:3.1.3

# Switch to root to install system dependencies
USER root

# Install system dependencies for matplotlib
RUN apt-get update && apt-get install -y \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Switch back to airflow user
USER airflow

# Copy requirements file
COPY requirements.txt /tmp/requirements.txt

# Install only additional dependencies not in base image
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Set working directory
WORKDIR /opt/airflow