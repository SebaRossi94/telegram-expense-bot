import axios, { AxiosInstance } from 'axios';
import { BotServiceClient, type Expense } from '../botClient';
import config from '../config';
import logger from '../middlewares/logging';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

// Mock logger
jest.mock('../middlewares/logging', () => ({
  __esModule: true,
  default: {
    debug: jest.fn(),
    error: jest.fn(),
    info: jest.fn(),
  },
}));

describe('BotServiceClient', () => {
  let client: BotServiceClient;
  let requestInterceptor: (config: unknown) => unknown;
  let requestErrorInterceptor: (error: unknown) => unknown;
  let responseInterceptor: (response: unknown) => unknown;
  let responseErrorInterceptor: (error: unknown) => unknown;

  const mockAxiosInstance = {
    create: jest.fn(),
    get: jest.fn(),
    post: jest.fn(),
    interceptors: {
      request: {
        use: jest.fn((onFulfilled, onRejected) => {
          requestInterceptor = onFulfilled;
          requestErrorInterceptor = onRejected;
        }),
      },
      response: {
        use: jest.fn((onFulfilled, onRejected) => {
          responseInterceptor = onFulfilled;
          responseErrorInterceptor = onRejected;
        }),
      },
    },
  };

  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
    // Setup axios mock
    mockedAxios.create.mockReturnValue(
      mockAxiosInstance as unknown as AxiosInstance,
    );
    // Create a new client instance
    client = new BotServiceClient();
  });

  describe('interceptors', () => {
    it('should log request details in debug level', () => {
      const mockConfig = {
        method: 'POST',
        url: '/test',
        data: { test: 'data' },
      };

      requestInterceptor(mockConfig);

      expect(logger.debug).toHaveBeenCalledWith('Bot Service Request:', {
        method: mockConfig.method,
        url: mockConfig.url,
        data: mockConfig.data,
      });
    });

    it('should log request errors', async () => {
      const mockError = new Error('Request failed');

      await expect(requestErrorInterceptor(mockError)).rejects.toThrow(
        'Request failed',
      );
      expect(logger.error).toHaveBeenCalledWith(
        'Bot Service Request Error:',
        mockError,
      );
    });

    it('should log response details in debug level', () => {
      const mockResponse = {
        status: 200,
        data: { success: true },
      };

      responseInterceptor(mockResponse);

      expect(logger.debug).toHaveBeenCalledWith('Bot Service Response:', {
        status: mockResponse.status,
        data: mockResponse.data,
      });
    });

    it('should log response errors', async () => {
      const mockError = {
        response: {
          status: 500,
          data: { error: 'Server error' },
        },
        message: 'Internal server error',
      };

      await expect(responseErrorInterceptor(mockError)).rejects.toEqual(
        mockError,
      );
      expect(logger.error).toHaveBeenCalledWith('Bot Service Response Error:', {
        status: mockError.response.status,
        data: mockError.response.data,
        message: mockError.message,
      });
    });

    it('should handle response errors without response object', async () => {
      const mockError = {
        message: 'Network error',
      };

      await expect(responseErrorInterceptor(mockError)).rejects.toEqual(
        mockError,
      );
      expect(logger.error).toHaveBeenCalledWith('Bot Service Response Error:', {
        status: undefined,
        data: undefined,
        message: mockError.message,
      });
    });
  });

  describe('constructor', () => {
    it('should create an axios instance with correct configuration', () => {
      expect(mockedAxios.create).toHaveBeenCalledWith({
        baseURL: config.BOT_SERVICE_URL,
        timeout: 30000,
        headers: {
          'Content-Type': 'application/json',
          [config.BOT_SERVICE_API_KEY_HEADER]:
            config.BOT_SERVICE_API_KEY_SECRET,
        },
      });
    });

    it('should setup request and response interceptors', () => {
      expect(mockAxiosInstance.interceptors.request.use).toHaveBeenCalled();
      expect(mockAxiosInstance.interceptors.response.use).toHaveBeenCalled();
    });
  });

  describe('processBotMessage', () => {
    const telegramId = '123456789';
    const message = 'Test message';

    it('should successfully process a bot message', async () => {
      const mockResponse = {
        status: 200,
        data: { id: 1, message: 'Success' },
      };
      mockAxiosInstance.post.mockResolvedValueOnce(mockResponse);

      const result = await client.processBotMessage(telegramId, message);

      expect(mockAxiosInstance.post).toHaveBeenCalledWith(
        `/v1/expenses/${telegramId}`,
        { message },
      );
      expect(result).toEqual({
        success: true,
        data: mockResponse.data,
      });
    });

    it('should handle non-200 response', async () => {
      const mockResponse = {
        status: 400,
        data: { error: 'Bad request' },
      };
      mockAxiosInstance.post.mockResolvedValueOnce(mockResponse);

      const result = await client.processBotMessage(telegramId, message);

      expect(result).toEqual({
        success: false,
        data: mockResponse.data,
      });
    });

    it('should handle service errors', async () => {
      mockAxiosInstance.post.mockRejectedValueOnce(new Error('Network error'));

      const result = await client.processBotMessage(telegramId, message);

      expect(result).toEqual({
        success: false,
        error: 'Service unavailable',
        message:
          'Bot service is currently unavailable. Please try again later.',
      });
    });
  });

  describe('addUserToWhitelist', () => {
    const telegramId = '123456789';

    it('should successfully add user to whitelist', async () => {
      const mockResponse = {
        status: 200,
        data: { telegram_id: telegramId },
      };
      mockAxiosInstance.post.mockResolvedValueOnce(mockResponse);

      const result = await client.addUserToWhitelist(telegramId);

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/v1/users', {
        telegram_id: telegramId,
      });
      expect(result).toEqual({
        success: true,
        telegram_id: telegramId,
      });
    });

    it('should handle non-200 response', async () => {
      const mockResponse = {
        status: 400,
        data: { error: 'User already exists' },
      };
      mockAxiosInstance.post.mockResolvedValueOnce(mockResponse);

      const result = await client.addUserToWhitelist(telegramId);

      expect(result).toEqual({
        success: false,
        telegram_id: telegramId,
      });
    });

    it('should handle service errors', async () => {
      mockAxiosInstance.post.mockRejectedValueOnce(new Error('Network error'));

      const result = await client.addUserToWhitelist(telegramId);

      expect(result).toEqual({
        success: false,
        telegram_id: telegramId,
      });
    });
  });

  describe('getUserExpenses', () => {
    const telegramId = '123456789';
    const mockExpenses: Expense[] = [
      {
        id: 1,
        user_id: 1,
        description: 'Test expense',
        amount: 100,
        category: 'food',
        created_at: new Date(),
        updated_at: new Date(),
      },
    ];

    it('should successfully get user expenses', async () => {
      const mockResponse = {
        status: 200,
        data: mockExpenses,
      };
      mockAxiosInstance.get.mockResolvedValueOnce(mockResponse);

      const result = await client.getUserExpenses(telegramId);

      expect(mockAxiosInstance.get).toHaveBeenCalledWith(
        `/v1/expenses/${telegramId}`,
      );
      expect(result).toEqual(mockExpenses);
    });

    it('should handle empty response', async () => {
      const mockResponse = {
        status: 200,
        data: null,
      };
      mockAxiosInstance.get.mockResolvedValueOnce(mockResponse);

      const result = await client.getUserExpenses(telegramId);

      expect(result).toEqual([]);
    });

    it('should handle service errors', async () => {
      mockAxiosInstance.get.mockRejectedValueOnce(new Error('Network error'));

      const result = await client.getUserExpenses(telegramId);

      expect(result).toEqual([]);
    });
  });

  describe('botServiceHealthCheck', () => {
    it('should return true when service is healthy', async () => {
      const mockResponse = {
        status: 200,
        data: { status: 'healthy' },
      };
      mockAxiosInstance.get.mockResolvedValueOnce(mockResponse);

      const result = await client.botServiceHealthCheck();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/health');
      expect(result).toBe(true);
    });

    it('should return false when service is unhealthy', async () => {
      const mockResponse = {
        status: 200,
        data: { status: 'unhealthy' },
      };
      mockAxiosInstance.get.mockResolvedValueOnce(mockResponse);

      const result = await client.botServiceHealthCheck();

      expect(result).toBe(false);
    });

    it('should handle service errors', async () => {
      mockAxiosInstance.get.mockRejectedValueOnce(new Error('Network error'));

      const result = await client.botServiceHealthCheck();

      expect(result).toBe(false);
    });
  });
});
