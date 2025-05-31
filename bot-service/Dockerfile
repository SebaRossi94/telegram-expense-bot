# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry && \
    poetry self add poetry-plugin-export

# Copy only dependency files
COPY pyproject.toml poetry.lock* ./

# Export dependencies
RUN if [ "$VERSION" ]; then \
    poetry export -f requirements.txt --output requirements.txt --without-hashes --without dev ; \
    else \
    poetry export -f requirements.txt --output requirements.txt --without-hashes --with dev ; \
    fi

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements from builder
COPY --from=builder /app/requirements.txt .

# Install runtime dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    rm -rf requirements.txt

# Copy only necessary files
COPY app ./app
COPY migrations ./migrations
COPY alembic.ini .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
