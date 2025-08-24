import { render, screen } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import AnalyticsDashboard from '../components/AnalyticsDashboard';

// Mock child components
vi.mock('../components/PostViewDynamicsChart', () => ({
  default: () => <div data-testid="post-view-dynamics-chart">PostViewDynamicsChart Mock</div>
}));

vi.mock('../components/TopPostsTable', () => ({
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
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders dashboard title correctly', () => {
    render(
      <TestWrapper>
        <AnalyticsDashboard />
      </TestWrapper>
    );

    expect(screen.getByText('Analytics Dashboard')).toBeInTheDocument();
  });

  it('renders dashboard phase indicator', () => {
    render(
      <TestWrapper>
        <AnalyticsDashboard />
      </TestWrapper>
    );

    expect(screen.getByText('📊 Rich Analytics Dashboard')).toBeInTheDocument();
  });

  it('renders navigation breadcrumbs', () => {
    render(
      <TestWrapper>
        <AnalyticsDashboard />
      </TestWrapper>
    );

    expect(screen.getByText('Bosh sahifa')).toBeInTheDocument();
    expect(screen.getByText('Analytics Dashboard')).toBeInTheDocument();
  });
});
