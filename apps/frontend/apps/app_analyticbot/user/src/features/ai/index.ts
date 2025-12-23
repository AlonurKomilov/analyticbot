/**
 * User AI Feature Module
 * Barrel export for all AI feature components
 * 
 * Structure similar to bot and mtproto-setup features:
 * - api/       - API client for user AI endpoints
 * - components/ - React components
 * - hooks/     - Custom hooks for state management
 * - types/     - TypeScript type definitions
 */

// Components
export * from './components';
export { UserAIDashboard } from './components';

// API
export * from './api';
export { UserAIAPI } from './api';

// Hooks
export * from './hooks';
export { useAIDashboard, useAIServices, useFullAIDashboard } from './hooks';

// Types
export * from './types';
