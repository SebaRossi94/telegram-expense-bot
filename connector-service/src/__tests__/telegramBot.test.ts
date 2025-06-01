import TelegramBot from 'node-telegram-bot-api';
import { BotServiceClient } from '../botClient';
import type { Expense } from '../botClient';

// Mock the entire node-telegram-bot-api module
jest.mock('node-telegram-bot-api');

// Mock the BotServiceClient
jest.mock('../botClient');

// Declare handler variables
let listHandler: (msg: unknown) => Promise<void>;
let addHandler: (msg: unknown, args: unknown) => Promise<void>;

// Create a global mock bot instance
const mockBot = {
  sendMessage: jest.fn(),
  onText: jest.fn().mockImplementation((regex, handler) => {
    if (regex.toString().includes('/list')) {
      listHandler = handler;
    } else if (regex.toString().includes('/add')) {
      addHandler = handler;
    }
  }),
};

// Mock the TelegramBot constructor
(TelegramBot as unknown as jest.Mock).mockImplementation(() => mockBot);

describe('TelegramBot', () => {
  let mockBotServiceClient: jest.Mocked<BotServiceClient>;

  beforeEach(() => {
    // Clear all mocks
    jest.clearAllMocks();

    // Setup BotServiceClient mock
    mockBotServiceClient = {
      getUserExpenses: jest.fn(),
      processBotMessage: jest.fn(),
      botServiceHealthCheck: jest.fn(),
    } as unknown as jest.Mocked<BotServiceClient>;

    (BotServiceClient as jest.Mock).mockImplementation(
      () => mockBotServiceClient,
    );

    // Import the module to trigger the handlers registration
    jest.isolateModules(async () => {
      await import('../telegramBot');
    });
  });

  describe('/list command', () => {
    const mockMsg = {
      chat: { id: 123 },
      from: { username: 'testUser' },
    };

    it('should send message with expenses when user has expenses', async () => {
      const mockExpenses: Expense[] = [
        {
          category: 'Food',
          description: 'Lunch',
          amount: 10,
          created_at: new Date(),
          updated_at: new Date(),
          id: 1,
          user_id: 1,
        },
        {
          category: 'Transport',
          description: 'Bus',
          amount: 5,
          created_at: new Date(),
          updated_at: new Date(),
          id: 2,
          user_id: 1,
        },
      ];

      mockBotServiceClient.getUserExpenses.mockResolvedValue(mockExpenses);

      await listHandler(mockMsg);

      expect(mockBot.sendMessage).toHaveBeenCalledWith(
        mockMsg.chat.id,
        'Food - Lunch - 10\nTransport - Bus - 5',
      );
    });

    it('should send appropriate message when user has no expenses', async () => {
      mockBotServiceClient.getUserExpenses.mockResolvedValue([]);

      await listHandler(mockMsg);

      expect(mockBot.sendMessage).toHaveBeenCalledWith(
        mockMsg.chat.id,
        'You have no expenses recorded yet.',
      );
    });

    it('should handle errors when fetching expenses', async () => {
      mockBotServiceClient.getUserExpenses.mockRejectedValue(
        new Error('API Error'),
      );

      await listHandler(mockMsg);

      expect(mockBot.sendMessage).toHaveBeenCalledWith(
        mockMsg.chat.id,
        'Error fetching your expenses ❌. Please try again later.',
      );
    });
  });

  describe('/add command', () => {
    const mockMsg = {
      chat: { id: 123, username: 'testUser' },
    };

    it('should successfully add an expense', async () => {
      const mockResponse = {
        success: true,
        data: { category: 'Food' },
      };

      mockBotServiceClient.processBotMessage.mockResolvedValue(mockResponse);

      await addHandler(mockMsg, ['/add food 10', 'food 10']);

      expect(mockBot.sendMessage).toHaveBeenCalledWith(
        mockMsg.chat.id,
        'Processing your expense...',
      );
      expect(mockBot.sendMessage).toHaveBeenCalledWith(
        mockMsg.chat.id,
        'Food expense added ✅',
      );
    });

    it('should handle failed expense addition', async () => {
      const mockResponse = {
        success: false,
        data: undefined,
      };

      mockBotServiceClient.processBotMessage.mockResolvedValue(mockResponse);

      await addHandler(mockMsg, ['/add invalid', 'invalid']);

      expect(mockBot.sendMessage).toHaveBeenCalledWith(
        mockMsg.chat.id,
        'Processing your expense...',
      );
      expect(mockBot.sendMessage).toHaveBeenCalledWith(
        mockMsg.chat.id,
        'Error adding your expense ❌. Please try again',
      );
    });

    it('should handle missing expense text', async () => {
      await addHandler(mockMsg, ['/add', null]);

      expect(mockBot.sendMessage).toHaveBeenCalledWith(
        mockMsg.chat.id,
        'Please write your expense',
      );
    });
  });
});
