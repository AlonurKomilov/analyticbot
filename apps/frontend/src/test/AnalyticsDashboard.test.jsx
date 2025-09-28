import { render, screen } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { server } from '../__mocks__/api/server.js';
import { http, HttpResponse } from 'msw';
import AnalyticsDashboard from '../components/dashboard/AnalyticsDashboard/AnalyticsDashboard';

// Mock child components (keep these for unit testing focus)
vi.mock('../components/charts/PostViewDynamics', () => ({
  default: () => <div data-testid="post-view-dynamics-chart">PostViewDynamicsChart Mock</div>
}));

vi.mock('../components/EnhancedTopPostsTable', () => ({
  default: () => <div data-testid="top-posts-table">TopPostsTable Mock</div>
}));

vi.mock('../components/BestTimeRecommender', () => ({
  default: () => <div data-testid="best-time-recommender">BestTimeRecommender Mock</div>
}));

const theme = createTheme();

const TestWrapper = ({ children }) => (
  <ThemeProvider theme={theme}>
    {children}
  </ThemeProvider>
);

describe('AnalyticsDashboard', () => {
  beforeEach(() => {
    server.resetHandlers();
    // Mock localStorage
    const localStorageMock = {
      getItem: vi.fn(() => null),
      setItem: vi.fn(),
      clear: vi.fn(),
      removeItem: vi.fn()
    };
    Object.defineProperty(window, 'localStorage', {
      value: localStorageMock,
      writable: true
    });
  });

  it('renders dashboard title correctly', async () => {
    render(
      <TestWrapper>
        <AnalyticsDashboard />
      </TestWrapper>
    );

    // Wait for component to load with MSW data
    await screen.findByText('Analytics Dashboard');
    expect(screen.getByText('Analytics Dashboard')).toBeInTheDocument();
  });

  it('renders content protection alert', async () => {
    render(
      <TestWrapper>
        <AnalyticsDashboard />
      </TestWrapper>
    );

    // Check that the content protection alert is present instead
    await screen.findByText(/Week 5-6 Content Protection Available/);
    expect(screen.getByText(/Week 5-6 Content Protection Available/)).toBeInTheDocument();
  });

  it('handles API error gracefully', async () => {
    // Override MSW to return error
    server.use(
      http.get('/api/initial-data', () => {
        return HttpResponse.error();
      })
    );

    render(
      <TestWrapper>
        <AnalyticsDashboard />
      </TestWrapper>
    );

    // Should show components or handle errors gracefully
    // Dashboard should still render even if API fails - components will handle their own error states
    expect(screen.getByText('Analytics Dashboard')).toBeInTheDocument();
  });
});
