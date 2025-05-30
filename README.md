# Telegram Expense Tracking Bot

A microservices-based Telegram bot system for tracking personal expenses through natural language messages.

## Architecture

The system consists of two main services:

1. **Bot Service** (Python-FastAPI): Processes messages, extracts expense data using LangChain LLM, and manages database operations
2. **Connector Service** (Node.js-Express): Handles Telegram API integration and forwards messages between Telegram and the Bot Service

## Features

- ✅ Natural language expense parsing ("Pizza 20 bucks" → categorized expense)
- ✅ Automatic expense categorization using AI
- ✅ User whitelist management
- ✅ Concurrent request handling
- ✅ Production-ready deployment configurations
- ✅ Comprehensive error handling and logging
- ✅ Database migrations and setup
- ✅ Docker containerization

## Quick Start

### Prerequisites

- Docker and Docker Compose
- PostgreSQL database (or use Supabase)
- Telegram Bot Token
- OpenAI API Key (or other LangChain-supported LLM)

### Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/SebaRossi94/telegram-expense-bot.git
cd telegram-expense-bot
```

2. Set up environment files:
```bash
# Bot Service
cp bot-service/.env.example bot-service/.env
# Edit bot-service/.env with your configuration

# Connector Service
cp connector-service/.env.example connector-service/.env
# Edit connector-service/.env with your configuration
```

3. Start the services:
```bash
docker-compose up -d
```

4. Run migrations
```
CMD + Shift + P -> Tasks: Run Task -> Run Migration

or

docker compose exec bot-service alembic upgrade head
```
5. Check services health:
   1. http://localhost:8000/health
   2. http://localhost:3000/health
6. Check bot service docs
   1. http://localhost:8000/docs

See individual service READMEs for detailed setup instructions:
- [Bot Service Setup](./bot-service/README.md)
- [Connector Service Setup](./connector-service/README.md)

## Usage

1. Add your Telegram user ID to the whitelist in the database
```
curl -X 'POST' \
  'http://localhost:8000/v1/users/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "telegram_id": "yourtelegramusername"
}'
```
2. Send expense messages to your bot. Use `/add` command:
   - "Coffee 5 dollars"
   - "Uber ride $15"
   - "Groceries 45 bucks"
   - "Netflix subscription 12.99"

The bot will automatically:
- Parse the amount and description
- Categorize the expense (Food, Transportation, Entertainment, etc.)
- Store it in the database
- Reply with confirmation: "[Category] expense added✅"

3. Check you added expenses with command `/list`