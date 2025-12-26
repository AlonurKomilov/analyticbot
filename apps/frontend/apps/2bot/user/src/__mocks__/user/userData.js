/**
 * User Mock Data
 * Separated from the main mockData.js for better organization
 */

import { DEFAULT_DEMO_USERNAME } from '../constants.js';

export const userData = {
  id: `${DEFAULT_DEMO_USERNAME}_123`,
  username: 'analytics_pro',
  first_name: 'Analytics',
  last_name: 'Pro',
  language_code: 'en'
};

export const planData = {
  name: 'Professional',
  maxChannels: 10,
  maxPostsPerMonth: 500,
  features: ['Advanced Analytics', 'AI Insights', 'Custom Branding', 'Priority Support']
};

export const systemStatusData = {
  botStatus: 'online',
  apiStatus: 'operational',
  analyticsStatus: 'processing',
  lastUpdate: new Date().toISOString()
};
