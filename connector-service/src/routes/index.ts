import express from 'express';
import healtRouter from './health';

const router = express.Router({ mergeParams: true });

router.use('', healtRouter)

export default router;