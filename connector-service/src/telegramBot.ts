import TelegramBot from 'node-telegram-bot-api';
import config from './config';
import { BotServiceClient } from './botClient';
import type { Expense } from './botClient';
import logger from './middlewares/logging';

export const telegramBot = new TelegramBot(config.TELEGRAM_BOT_TOKEN, { polling: true });


telegramBot.onText(/\/list/, async (msg) => {
  const chatId = msg.chat.id;
  const telegramId = msg.from?.username
  const botServiceClient = new BotServiceClient()
  const expenses = await botServiceClient.getUserExpenses(telegramId)
  const parsedExpenses = expenses.map((expense: Expense) => `${expense.category} - ${expense.description} - ${expense.amount}`)
  telegramBot.sendMessage(chatId, parsedExpenses.join('\n'));
});

telegramBot.onText(/\/add (.*)/, async (msg, match) => {
  const chatId = msg.chat.id;
  const telegramId = msg.chat.username;
  if (match[1] === null) {
    telegramBot.sendMessage(chatId, 'Please write your expense')
  }
  logger.info(`${telegramId} is trying to add expense with text ${match[1]}`)
  const botServiceClient = new BotServiceClient()
  const response = await botServiceClient.processBotMessage(telegramId, match[1])
  if (response.success) {
    telegramBot.sendMessage(chatId, `${response.data?.category} expense added ✅`);

  } else {
    telegramBot.sendMessage(chatId, 'Error adding your expense ❌. Please try again');
  }
});