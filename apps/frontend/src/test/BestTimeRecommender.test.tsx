import { render, screen } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import BestTimeRecommender from '../components/analytics/BestTimeRecommender/BestTimeRecommender';
import React from 'react';

const theme = createTheme();

interface TestWrapperProps {
  children: React.ReactNode;
}

const TestWrapper: React.FC<TestWrapperProps> = ({ children }) => (
  <ThemeProvider theme={theme}>
    {children}
  </ThemeProvider>
);

// Mock data
const mockRecommenderData = {
  recommendations: [
    {
      dayOfWeek: "Monday",
      timeRange: "09:00-11:00",
      averageEngagement: 8.5,
      confidence: 0.92,
      reasons: ["High audience activity", "Low competition"]
    },
    {
      dayOfWeek: "Wednesday",
      timeRange: "14:00-16:00",
      averageEngagement: 7.8,
      confidence: 0.87,
      reasons: ["Peak viewing hours", "Active user base"]
    },
    {
      dayOfWeek: "Friday",
      timeRange: "18:00-20:00",
      averageEngagement: 9.1,
      confidence: 0.95,
      reasons: ["Weekend preparation", "Social media peak"]
    }
  ]
};

describe('BestTimeRecommender', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Mock fetch API
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockRecommenderData),
      } as Response)
    );
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders without crashing', () => {
    render(
      <TestWrapper>
        <BestTimeRecommender />
      </TestWrapper>
    );

    // Component should render successfully - check for main heading
    expect(screen.getByText('Best Time to Post Recommender')).toBeInTheDocument();
  });

  it('shows no recommendations alert initially', () => {
    render(
      <TestWrapper>
        <BestTimeRecommender />
      </TestWrapper>
    );

    // Component shows "no recommendations" alert instead of loading state
    expect(screen.getByText('No recommendations available for the selected filters')).toBeInTheDocument();
  });

  it('renders time frame filter', () => {
    render(
      <TestWrapper>
        <BestTimeRecommender />
      </TestWrapper>
    );

    expect(screen.getAllByText('Vaqt oralig\'i')).toHaveLength(2); // label and legend
  });
});
