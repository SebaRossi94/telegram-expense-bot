import TelegramBot from 'node-telegram-bot-api';
import express from 'express';
import config from './config';
import router from './routes/index';
import helmet from 'helmet';
import cors from 'cors';
import compression from 'compression';
import rateLimit from 'express-rate-limit';

const telegramBot = new TelegramBot(config.TELEGRAM_BOT_TOKEN, { polling: true });
const app = express();

// Security middleware
app.use(helmet());
app.use(cors());
app.use(compression());

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 1000, // Limit each IP to 1000 requests per windowMs
  message: 'Too many requests from this IP',
  standardHeaders: true,
  legacyHeaders: false,
});
app.use(limiter);

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

//  Listen for any kind of message. There are different kinds of
//  messages.
 telegramBot.on('message', (msg) => {
   const chatId = msg.chat.id;

// send a message to the chat acknowledging receipt of their message
   console.log(msg);
   telegramBot.sendMessage(chatId, 'Hello there');
 });

app.get('/health', (_, res) => {res.json({status: 'ok'})})
app.use(router)

export default app;