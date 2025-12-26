/**
 * MSW Server Setup for Testing
 */

import { setupServer } from 'msw/node';
import { handlers } from './handlers.js';

// Setup MSW server with our handlers
export const server = setupServer(...handlers);
