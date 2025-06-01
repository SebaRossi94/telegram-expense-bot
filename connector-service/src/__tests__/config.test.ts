import config from '../config';

describe('Config', () => {
  const originalEnv = process.env;

  beforeEach(() => {
    jest.resetModules();
    process.env = {
      NODE_ENV: 'development', // Explicitly set this for the test
    };
  });

  afterAll(() => {
    process.env = originalEnv;
  });

  it('should use default values when environment variables are not set', () => {
    jest.isolateModules(async () => {
      const { default: newConfig } = await import('../config');
      expect(newConfig.PORT).toBe(3000);
      expect(newConfig.NODE_ENV).toBe('development');
      expect(newConfig.LOG_LEVEL).toBe('info');
      expect(newConfig.BOT_SERVICE_URL).toBe('http://bot-service:8000');
    });
  });

  it('should use environment variables when they are set', () => {
    process.env.PORT = '4000';
    process.env.NODE_ENV = 'production';
    process.env.LOG_LEVEL = 'debug';
    process.env.BOT_SERVICE_URL = 'http://custom-service:5000';

    jest.isolateModules(async () => {
      const { default: newConfig } = await import('../config');
      expect(newConfig.PORT).toBe(4000);
      expect(newConfig.NODE_ENV).toBe('production');
      expect(newConfig.LOG_LEVEL).toBe('debug');
      expect(newConfig.BOT_SERVICE_URL).toBe('http://custom-service:5000');
    });
  });

  it('should have required Telegram configuration', () => {
    expect(config.TELEGRAM_API_URL).toBe('https://api.telegram.org/bot');
    expect(config).toHaveProperty('TELEGRAM_BOT_TOKEN');
    expect(config).toHaveProperty('BOT_SERVICE_API_KEY_SECRET');
    expect(config).toHaveProperty('BOT_SERVICE_API_KEY_HEADER');
  });
});
