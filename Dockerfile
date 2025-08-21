# Multi-stage Dockerfile for Landscape Architecture Tool Backend
# 
# IMPORTANT: When making changes to cache/performance modules, 
# it's recommended to build with --no-cache to ensure clean Python module imports:
# docker build --no-cache -t landscape-architecture-tool .
#
# Stage 1: Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies with network timeout and retry handling
RUN pip install --no-cache-dir --upgrade pip --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org && \
    pip install --no-cache-dir -r requirements.txt --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --timeout 60 --retries 3 && \
    pip install --no-cache-dir psycopg2-binary gunicorn --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --timeout 60 --retries 3

# Copy dependency validator for build-time validation
COPY src/utils/dependency_validator.py /tmp/dependency_validator.py

# Validate critical dependencies were installed successfully
RUN python -c "
import sys
sys.path.insert(0, '/tmp')
from dependency_validator import DependencyValidator
validator = DependencyValidator()
critical_ok, missing = validator.validate_critical_dependencies()
if not critical_ok:
    print('CRITICAL: Docker build failed - missing dependencies:', missing)
    exit(1)
print('✅ All critical dependencies validated in Docker build')
"

# Stage 2: Production stage
FROM python:3.11-slim as production

WORKDIR /app

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && \
    mkdir -p /app/logs /app/src/database && \
    chown -R app:app /app

# Copy application code
COPY --chown=app:app . .

# Switch to non-root user
USER app

# Create necessary directories
RUN mkdir -p src/database logs

# Set environment variables
ENV FLASK_APP=src.main:create_app
ENV FLASK_ENV=production
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run database migrations and start application
CMD ["sh", "-c", "flask db upgrade 2>/dev/null || true && gunicorn -c gunicorn.conf.py wsgi:application"]

