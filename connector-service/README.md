# Connector Service

The Connector Service acts as the interface between the Telegram API and the Bot Service. It handles webhook management, message routing, and response formatting.

## Features

- Telegram Bot API integration
- Message routing to Bot Service
- Response formatting and delivery
- Error handling and logging
- Health monitoring

## Setup

### Requirements

- Node.js 22+ (LTS)
- Telegram Bot Token
- Bot Service URL

### Installation

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start the service:
```bash
npm start
```

### Development

```bash
npm run dev
```

## Environment Variables

- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from @BotFather
- `BOT_SERVICE_URL`: URL of the Bot Service (e.g., http://localhost:8000)
- `PORT`: Service port (default: 3000)
- `NODE_ENV`: Environment (development/production)
- `LOG_LEVEL`: Logging level (debug/info/warn/error)
