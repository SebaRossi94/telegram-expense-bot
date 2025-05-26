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
};

export default config;
