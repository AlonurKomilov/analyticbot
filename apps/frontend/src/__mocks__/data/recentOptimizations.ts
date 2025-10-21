/**
 * Mock Recent Optimizations Data
 * Provides mock data for content optimization history in demo mode
 */

export interface Optimization {
  id: number;
  content: string;
  improvement: string;
  timestamp: string;
  status?: 'completed' | 'pending' | 'failed';
}

/**
 * Generate mock recent optimizations
 */
export const mockOptimizations: Optimization[] = [
  {
    id: 1,
    content: 'Product Launch Announcement',
    improvement: '+25%',
    timestamp: '2 minutes ago',
    status: 'completed'
  },
  {
    id: 2,
    content: 'Weekly Newsletter Content',
    improvement: '+18%',
    timestamp: '15 minutes ago',
    status: 'completed'
  },
  {
    id: 3,
    content: 'Blog Post Introduction',
    improvement: '+32%',
    timestamp: '1 hour ago',
    status: 'completed'
  },
  {
    id: 4,
    content: 'Social Media Post',
    improvement: '+15%',
    timestamp: '3 hours ago',
    status: 'completed'
  },
  {
    id: 5,
    content: 'Email Campaign Subject',
    improvement: '+28%',
    timestamp: '5 hours ago',
    status: 'completed'
  }
];

/**
 * Generate dynamic mock optimizations based on time
 */
export const generateMockOptimizations = (count: number = 3): Optimization[] => {
  const templates = [
    { content: 'Product Launch Announcement', improvement: '+25%' },
    { content: 'Weekly Newsletter Content', improvement: '+18%' },
    { content: 'Blog Post Introduction', improvement: '+32%' },
    { content: 'Social Media Post', improvement: '+15%' },
    { content: 'Email Campaign Subject', improvement: '+28%' },
    { content: 'Customer Testimonial Post', improvement: '+22%' },
    { content: 'Tutorial Video Description', improvement: '+19%' },
    { content: 'Landing Page Headline', improvement: '+35%' }
  ];

  const timeOffsets = [
    '2 minutes ago',
    '15 minutes ago',
    '1 hour ago',
    '3 hours ago',
    '5 hours ago',
    '1 day ago',
    '2 days ago'
  ];

  return templates
    .slice(0, Math.min(count, templates.length))
    .map((template, index) => ({
      id: index + 1,
      ...template,
      timestamp: timeOffsets[index] || `${index} days ago`,
      status: 'completed' as const
    }));
};
