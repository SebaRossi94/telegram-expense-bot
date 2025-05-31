/**
 * Configuration management for the Connector Service
 */

import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

interface Config {
  TELEGRAM_BOT_TOKEN: string;
  TELEGRAM_API_URL: string;
  BOT_SERVICE_URL: string;
  PORT: number;
  NODE_ENV: string;
  LOG_LEVEL: string;
  BOT_SERVICE_API_KEY_SECRET: string;
  BOT_SERVICE_API_KEY_HEADER: string;
}

const config: Config = {
  // Telegram Bot Configuration
  // biome-ignore lint/style/noNonNullAssertion: <explanation>
  TELEGRAM_BOT_TOKEN: process.env.TELEGRAM_BOT_TOKEN!,
  TELEGRAM_API_URL: 'https://api.telegram.org/bot',

  // Bot Service Configuration
  BOT_SERVICE_URL: process.env.BOT_SERVICE_URL || 'http://bot-service:8000',

  // Server Configuration
  PORT: Number.parseInt(process.env.PORT || '3000'),
  NODE_ENV: process.env.NODE_ENV || 'development',

  // Logging Configuration
  LOG_LEVEL: process.env.LOG_LEVEL || 'info',

  // Bot Service API Key Configuration
  BOT_SERVICE_API_KEY_SECRET: process.env.BOT_SERVICE_API_KEY_SECRET!,
  BOT_SERVICE_API_KEY_HEADER: process.env.BOT_SERVICE_API_KEY_HEADER!,
};

export default config;
