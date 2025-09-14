/**
 * User Mock Data
 * Separated from the main mockData.js for better organization
 */

export const userData = {
  id: 'demo_user_123',
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