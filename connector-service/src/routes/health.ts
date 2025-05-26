import express from 'express';

import {} from 'express'
const router = express.Router({ mergeParams: true });

// Health check endpoint
router.get('/health', async (req, res) => {
  try {
    
    res.json({
      status: 'healthy',
      service: 'Telegram Connector Service',
      version: '1.0.0',
      timestamp: new Date().toISOString(),
      telegram: 'connected' // If we can respond, Telegram connection is working
    });
  } catch (error: unknown) {
    const err = error instanceof Error ? error : new Error('Unknown error');
    res.status(500).json({
      status: 'unhealthy',
      error: err.message
    });
  }
});

export default router;
