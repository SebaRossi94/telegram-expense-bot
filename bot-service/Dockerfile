FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry 

RUN poetry self add poetry-plugin-export

COPY ./pyproject.toml ./poetry.lock* /app/

RUN if [ "$VERSION" ]; then \
    poetry export -f requirements.txt --output /app/requirements.txt --without-hashes --without dev ; \
    else \
    poetry export -f requirements.txt --output /app/requirements.txt --without-hashes --with dev ; \
    fi

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

