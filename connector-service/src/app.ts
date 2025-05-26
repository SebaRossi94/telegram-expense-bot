import TelegramBot from 'node-telegram-bot-api';
import express from 'express';
import config from './config';
import router from './routes/index';

const bot = new TelegramBot(config.TELEGRAM_BOT_TOKEN, { polling: true });
const app = express();

//  Listen for any kind of message. There are different kinds of
//  messages.
 bot.on('message', (msg) => {
   const chatId = msg.chat.id;

// send a message to the chat acknowledging receipt of their message
   console.log(msg);
   bot.sendMessage(chatId, 'Hello there');
 });

app.get('/health', (_, res) => {res.json({status: 'ok'})})
app.use(router)

export default app;