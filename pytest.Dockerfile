# CI/Local test runner image
FROM python:3.12-slim

# System deps for psycopg2 and building wheels
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only dependency manifest first (better build cache)
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt \
    && pip install --no-cache-dir pytest pytest-cov pytest-mock

# Copy source
COPY . /app


# Run tests by default; override with command in compose if needed
CMD ["python", "-m", "pytest", "-v", "--maxfail=1"]
