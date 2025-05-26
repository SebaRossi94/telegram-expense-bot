# Bot Service

The Bot Service is responsible for processing expense messages, extracting structured data using LangChain LLM, and managing database operations.

## Features

- Natural language processing for expense extraction
- Automatic expense categorization
- User authentication via whitelist
- Concurrent request handling
- PostgreSQL database integration
- Comprehensive logging

## Setup

### Requirements

- Python 3.11+
- PostgreSQL database
- OpenAI API key (or other LangChain-supported LLM)

### Local Development

1. Set up virtual env
   `poetry install`
2. Select python interpreter from newly created venv

## Environment Variables

- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `POSTGRES_DB`
- `DATABASE_URL`
- `OPENAI_API_KEY`
- `HUGGINGFACEHUB_MODEL`
- `HUGGINGFACEHUB_API_TOKEN`
- `LLM_MODEL`
- `HOST`
- `PORT`
- `LOG_LEVEL`
- `DEV`
- `EXPENSE_CATEGORIES`
