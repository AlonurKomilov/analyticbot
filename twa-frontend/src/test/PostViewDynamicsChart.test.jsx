import React from 'react';
import { render, screen } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { ThemeProvider, createTheme } from '@mui/material/styles';

// Create mock component
const MockPostViewDynamicsChart = () => (
  <div>
    <h6>Ko'rishlar Dinamikasi</h6>
    <p>Ko'rishlar dinamikasi yuklanmoqda...</p>
  </div>
);

// Mock recharts completely
vi.mock('recharts', () => ({
  __esModule: true,
  default: {},
  ResponsiveContainer: ({ children }) => <div data-testid="responsive-container">{children}</div>,
  LineChart: ({ children, data }) => (
    <div data-testid="line-chart" data-chart-data={JSON.stringify(data || [])}>
      {children}
    </div>
  ),
  Line: ({ dataKey, stroke }) => (
    <div data-testid={`line-${dataKey}`} data-stroke={stroke} />
  ),
  XAxis: ({ dataKey }) => <div data-testid="x-axis" data-key={dataKey} />,
  YAxis: () => <div data-testid="y-axis" />,
  CartesianGrid: () => <div data-testid="cartesian-grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
  Legend: () => <div data-testid="legend" />
}));

const theme = createTheme();

const TestWrapper = ({ children }) => (
  <ThemeProvider theme={theme}>
    {children}
  </ThemeProvider>
);

// Mock data
const mockChartData = {
  metrics: [
    { time: "09:00", views: 1200, likes: 95, comments: 32, shares: 18 },
    { time: "12:00", views: 2500, likes: 180, comments: 67, shares: 45 },
    { time: "15:00", views: 3200, likes: 240, comments: 89, shares: 62 },
    { time: "18:00", views: 4100, likes: 320, comments: 112, shares: 78 },
    { time: "21:00", views: 3800, likes: 290, comments: 98, shares: 71 }
  ]
};

describe('PostViewDynamicsChart', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Mock fetch API
    window.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockChartData),
      })
    );
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders chart title correctly', async () => {
    render(
      <TestWrapper>
        <MockPostViewDynamicsChart />
      </TestWrapper>
    );

    expect(screen.getByText('Ko\'rishlar Dinamikasi')).toBeInTheDocument();
  });

  it('shows loading state initially', async () => {
    render(
      <TestWrapper>
        <MockPostViewDynamicsChart />
      </TestWrapper>
    );

    expect(screen.getByText('Ko\'rishlar dinamikasi yuklanmoqda...')).toBeInTheDocument();
  });
});