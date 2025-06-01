import request from 'supertest';
import express from 'express';
import healthRouter from '../../routes/health';
import { BotServiceClient } from '../../botClient';

// Mock the BotServiceClient
jest.mock('../../botClient');

describe('Health Routes', () => {
  let app: express.Application;
  let mockBotServiceHealthCheck: jest.Mock;

  beforeEach(() => {
    // Clear all mocks
    jest.clearAllMocks();

    // Create a new express app and use the health router
    app = express();
    app.use(express.json());
    app.use('', healthRouter);

    // Setup mock function
    mockBotServiceHealthCheck = jest.fn();

    // Setup BotServiceClient mock implementation
    (BotServiceClient as jest.Mock).mockImplementation(() => ({
      botServiceHealthCheck: mockBotServiceHealthCheck,
    }));
  });

  describe('GET /health', () => {
    it('should return healthy status when all services are up', async () => {
      mockBotServiceHealthCheck.mockResolvedValue(true);

      const response = await request(app).get('/health');

      expect(response.status).toBe(200);
      expect(response.body).toEqual({
        status: 'healthy',
        service: 'Telegram Connector Service',
        version: '1.0.0',
        timestamp: expect.any(String),
        botService: 'connected',
        telegram: 'connected',
      });
      expect(mockBotServiceHealthCheck).toHaveBeenCalled();
    });

    it('should show bot service as disconnected when health check fails', async () => {
      mockBotServiceHealthCheck.mockResolvedValue(false);

      const response = await request(app).get('/health');

      expect(response.status).toBe(200);
      expect(response.body).toEqual({
        status: 'healthy',
        service: 'Telegram Connector Service',
        version: '1.0.0',
        timestamp: expect.any(String),
        botService: 'disconnected',
        telegram: 'connected',
      });
      expect(mockBotServiceHealthCheck).toHaveBeenCalled();
    });

    it('should return unhealthy status when bot service throws error', async () => {
      const errorMessage = 'Bot service connection error';
      mockBotServiceHealthCheck.mockRejectedValue(new Error(errorMessage));

      const response = await request(app).get('/health');

      expect(response.status).toBe(500);
      expect(response.body).toEqual({
        status: 'unhealthy',
        error: errorMessage,
      });
      expect(mockBotServiceHealthCheck).toHaveBeenCalled();
    });
  });
});
