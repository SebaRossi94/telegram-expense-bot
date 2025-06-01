import axios, {
  type InternalAxiosRequestConfig,
  type AxiosInstance,
  type AxiosResponse,
} from 'axios';
import config from './config';
import logger from './middlewares/logging';

export interface Expense {
  created_at: Date;
  updated_at: Date;
  id: number;
  user_id: number;
  description: string;
  amount: number;
  category: string;
}

interface ProcessBotMessageResponse {
  success: boolean;
  error?: string;
  message?: string;
  data?: Record<string, unknown> | Expense;
  [key: string]: unknown;
}

interface WhitelistResponse {
  success: boolean;
  telegram_id: string;
}

export class BotServiceClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: config.BOT_SERVICE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
        [config.BOT_SERVICE_API_KEY_HEADER]: config.BOT_SERVICE_API_KEY_SECRET,
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        logger.debug('Bot Service Request:', {
          method: config.method,
          url: config.url,
          data: config.data,
        });
        return config;
      },
      (error) => {
        logger.error('Bot Service Request Error:', error);
        return Promise.reject(error);
      },
    );

    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        logger.debug('Bot Service Response:', {
          status: response.status,
          data: response.data,
        });
        return response;
      },
      (error) => {
        logger.error('Bot Service Response Error:', {
          status: error.response?.status,
          data: error.response?.data,
          message: error.message,
        });
        return Promise.reject(error);
      },
    );
  }

  async processBotMessage(
    telegramId: string,
    message: string,
  ): Promise<ProcessBotMessageResponse> {
    try {
      const response = await this.client.post(`/v1/expenses/${telegramId}`, {
        message,
      });
      if (response?.status === 200) {
        return {
          success: true,
          data: response.data,
        };
      }
      return {
        success: false,
        data: response.data,
      };
    } catch (error: unknown) {
      logger.error('Failed to process message through Bot Service:', error);
      return {
        success: false,
        error: 'Service unavailable',
        message:
          'Bot service is currently unavailable. Please try again later.',
      };
    }
  }

  async addUserToWhitelist(telegramId: string): Promise<WhitelistResponse> {
    try {
      const response = await this.client.post('/v1/users', {
        telegram_id: telegramId,
      });
      if (response?.status === 200) {
        return {
          success: true,
          telegram_id: telegramId,
        };
      }
      return {
        success: false,
        telegram_id: telegramId,
      };
    } catch (error) {
      logger.error('Failed to add user to whitelist:', error);
      return {
        success: false,
        telegram_id: telegramId,
      };
    }
  }

  async getUserExpenses(telegramId: string): Promise<Expense[]> {
    try {
      logger.info('Getting user expenses:', telegramId);
      const response = await this.client.get(`/v1/expenses/${telegramId}`);
      return response.data || [];
    } catch (error) {
      logger.error('Failed to get user expenses:', error);
      return [];
    }
  }

  async botServiceHealthCheck(): Promise<boolean> {
    try {
      const response = await this.client.get('/health');
      return response.data.status === 'healthy';
    } catch (error) {
      logger.error('Bot Service health check failed:', error);
      return false;
    }
  }
}
