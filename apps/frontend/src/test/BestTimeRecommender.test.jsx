import { render, screen } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import BestTimeRecommender from '../components/analytics/BestTimeRecommender/BestTimeRecommender';

const theme = createTheme();

const TestWrapper = ({ children }) => (
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
    window.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockRecommenderData),
      })
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

    // Component should render successfully
    expect(screen.getByRole('progressbar', { name: 'Loading recommendations' })).toBeInTheDocument();
  });

  it('shows loading state initially', () => {
    render(
      <TestWrapper>
        <BestTimeRecommender />
      </TestWrapper>
    );

    expect(screen.getByText('Loading AI recommendations...')).toBeInTheDocument();
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
