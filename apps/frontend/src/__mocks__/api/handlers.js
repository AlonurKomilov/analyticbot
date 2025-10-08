/**
 * MSW API Handlers for Testing
 *
 * This file defines mock API endpoints using Mock Service Worker
 * for realistic API mocking in tests.
 */

import { http, HttpResponse } from 'msw';
import {
  getMockPostDynamics,
  getMockTopPosts,
  getMockBestTime,
  getMockEngagementMetrics,
  getMockInitialData
} from '../index.js';

export const handlers = [
  // Health check endpoint for DataSourceSettings
  http.get('https://84dp9jc9-11400.euw.devtunnels.ms/health', () => {
    return HttpResponse.json({
      status: 'ok',
      timestamp: new Date().toISOString()
    });
  }),

  // Initial data endpoint
  http.get('/api/initial-data', async () => {
    const data = await getMockInitialData();
    return HttpResponse.json(data);
  }),

  // Analytics endpoints
  http.get('/api/v2/analytics/channels/:channelId/post-dynamics', async ({ request }) => {
    const url = new URL(request.url);
    const period = url.searchParams.get('period') || '24h';
    const data = await getMockPostDynamics(period);
    return HttpResponse.json(data);
  }),

  http.get('/api/v2/analytics/channels/:channelId/top-posts', async ({ request, params }) => {
    const url = new URL(request.url);

    // Handle both period-based and date range-based requests
    let period = url.searchParams.get('period') || 'today';
    const from = url.searchParams.get('from');
    const to = url.searchParams.get('to');
    const sortBy = url.searchParams.get('sort') || 'views';

    // If using date ranges, convert to period
    if (from && to) {
      const daysDiff = Math.ceil((new Date(to) - new Date(from)) / (1000 * 60 * 60 * 24));
      if (daysDiff <= 1) period = 'today';
      else if (daysDiff <= 7) period = 'week';
      else if (daysDiff <= 30) period = 'month';
      else period = 'week';
    }

    const { channelId } = params;
    console.log('MSW: Top posts request for channel:', channelId, 'period:', period, 'sortBy:', sortBy);

    const data = await getMockTopPosts(period, sortBy);
    return HttpResponse.json(data);
  }),

  http.get('/api/v2/analytics/channels/:channelId/best-times', async ({ request }) => {
    const url = new URL(request.url);
    const timeframe = url.searchParams.get('timeframe') || 'week';
    const data = await getMockBestTime(timeframe);
    return HttpResponse.json(data);
  }),

  http.get('/api/v2/analytics/channels/:channelId/engagement', async ({ request }) => {
    const url = new URL(request.url);
    const period = url.searchParams.get('period') || '7d';
    const data = await getMockEngagementMetrics(period);
    return HttpResponse.json(data);
  }),

  // Health check endpoint
  http.get('/health', () => {
    return HttpResponse.json({ status: 'ok', timestamp: new Date().toISOString() });
  }),

  // Error simulation endpoints for testing
  http.get('/api/test/error', () => {
    return HttpResponse.error();
  }),

  http.get('/api/test/timeout', async () => {
    // Simulate timeout
    await new Promise(resolve => setTimeout(resolve, 10000));
    return HttpResponse.json({ data: 'delayed' });
  })
];
