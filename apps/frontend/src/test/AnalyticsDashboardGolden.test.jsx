/**
 * Golden Standard Test Example - AnalyticsDashboard
 *
 * This demonstrates the ideal testing patterns for this project:
 * - Clean component isolation using MSW
 * - No mixed production/test logic
 * - Realistic API simulation
 * - Proper error handling testing
 * - Accessibility testing integration
 */

import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { server } from '../__mocks__/api/server.js';
import { http, HttpResponse } from 'msw';
import AnalyticsDashboard from '../components/dashboard/AnalyticsDashboard/AnalyticsDashboard';
import { useAppStore } from '../store/appStore';

// Test utilities
const TestWrapper = ({ children }) => (
  <ThemeProvider theme={createTheme()}>
    {children}
  </ThemeProvider>
);

// Helper to set store data source for tests
const setTestDataSource = (source) => {
  useAppStore.getState().setDataSource(source);
};

describe('AnalyticsDashboard - Golden Standard Test', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset store to default mock state
    setTestDataSource('mock');
    localStorage.clear();
  });

  describe('Data Loading', () => {
    it('displays loading state initially', () => {
      render(
        <TestWrapper>
          <AnalyticsDashboard />
        </TestWrapper>
      );

      // Should show loading indicators
      expect(screen.getByTestId('loading-overlay')).toBeInTheDocument();
    });

    it('loads and displays analytics data successfully', async () => {
      render(
        <TestWrapper>
          <AnalyticsDashboard />
        </TestWrapper>
      );

      // Wait for data to load
      await waitFor(() => {
        expect(screen.getByText('Analytics Dashboard')).toBeInTheDocument();
      }, { timeout: 3000 });

      // Verify main sections are rendered
      expect(screen.getByText('📊 Rich Analytics Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Post View Dynamics - Last 30 Days')).toBeInTheDocument();
    });
  });

  describe('API Error Handling', () => {
    it('shows user prompt dialog when API fails', async () => {
      // Setup MSW to simulate API failure
      server.use(
        http.get('/api/initial-data', () => {
          return HttpResponse.error();
        })
      );

      // Force store to use API data source before rendering
      setTestDataSource('api');

      render(
        <TestWrapper>
          <AnalyticsDashboard />
        </TestWrapper>
      );

      // Manually trigger fetchData to simulate API failure
      await waitFor(async () => {
        const state = useAppStore.getState();
        await state.fetchData('api');
      });

      // Wait for error dialog to appear
      await waitFor(() => {
        expect(screen.getByText('API Connection Failed')).toBeInTheDocument();
      });

      expect(screen.getByText('Unable to connect to the analytics API server.')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Try Again/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Use Demo Data/i })).toBeInTheDocument();
    });

    it('allows user to retry connection', async () => {
      let failCount = 0;
      server.use(
        http.get('/api/initial-data', () => {
          failCount++;
          if (failCount === 1) {
            return HttpResponse.error();
          }
          return HttpResponse.json({
            user: { username: 'test_user' },
            channels: [],
            scheduled_posts: [],
            plan: { name: 'Test Plan' }
          });
        })
      );

      // Force store to use API data source before rendering
      setTestDataSource('api');

      render(
        <TestWrapper>
          <AnalyticsDashboard />
        </TestWrapper>
      );

      // Wait for error dialog
      await waitFor(() => {
        expect(screen.getByText('API Connection Failed')).toBeInTheDocument();
      });

      // Click retry button
      fireEvent.click(screen.getByRole('button', { name: /Try Again/i }));

      // Dialog should close and data should load
      await waitFor(() => {
        expect(screen.queryByText('API Connection Failed')).not.toBeInTheDocument();
      });
    });

    it('allows user to switch to demo data', async () => {
      server.use(
        http.get('/api/initial-data', () => {
          return HttpResponse.error();
        })
      );

      // Force store to use API data source before rendering
      setTestDataSource('api');

      render(
        <TestWrapper>
          <AnalyticsDashboard />
        </TestWrapper>
      );

      // Wait for error dialog
      await waitFor(() => {
        expect(screen.getByText('API Connection Failed')).toBeInTheDocument();
      });

      // Click "Use Demo Data" button
      fireEvent.click(screen.getByRole('button', { name: /Use Demo Data/i }));

      // Dialog should close and demo data should load
      await waitFor(() => {
        expect(screen.queryByText('API Connection Failed')).not.toBeInTheDocument();
      });

      // Should show demo data indicator
      await waitFor(() => {
        expect(screen.getByText(/Demo Data/i)).toBeInTheDocument();
      });
    });
  });

  describe('User Interaction', () => {
    beforeEach(async () => {
      render(
        <TestWrapper>
          <AnalyticsDashboard />
        </TestWrapper>
      );

      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByText('Analytics Dashboard')).toBeInTheDocument();
      });
    });

    it('allows switching between tabs', async () => {
      // Click on "Top Posts" tab
      fireEvent.click(screen.getByRole('tab', { name: /Top Posts/i }));

      await waitFor(() => {
        expect(screen.getByText(/Top Posts/)).toBeInTheDocument();
      });

      // Click on "AI Time Recommendations" tab
      fireEvent.click(screen.getByRole('tab', { name: /AI Time Recommendations/i }));

      await waitFor(() => {
        expect(screen.getByText(/AI Time Recommendations/)).toBeInTheDocument();
      });
    });

    it('handles refresh functionality', async () => {
      // Find and click refresh button (speed dial menuitem)
      const refreshButton = screen.getByRole('menuitem', { name: /refresh/i });
      fireEvent.click(refreshButton);

      // Should show loading state briefly
      expect(screen.getByTestId('loading-overlay')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper heading structure', async () => {
      render(
        <TestWrapper>
          <AnalyticsDashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
      });

      // Should have proper heading hierarchy
      const headings = screen.getAllByRole('heading');
      expect(headings.length).toBeGreaterThan(0);
    });

    it('has proper tab navigation', async () => {
      render(
        <TestWrapper>
          <AnalyticsDashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByRole('tablist')).toBeInTheDocument();
      });

      const tabs = screen.getAllByRole('tab');
      expect(tabs.length).toBeGreaterThan(0);

      // Each tab should be keyboard navigable
      tabs.forEach(tab => {
        expect(tab).toHaveAttribute('tabindex');
      });
    });

    it('has proper ARIA labels', async () => {
      render(
        <TestWrapper>
          <AnalyticsDashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByRole('main')).toBeInTheDocument();
      });

      // Speed dial should have proper accessibility
      expect(screen.getByLabelText(/actions/i)).toBeInTheDocument();
    });
  });

  describe('Performance', () => {
    it('renders without unnecessary re-renders', async () => {
      const renderSpy = vi.fn();

      const TestComponent = () => {
        renderSpy();
        return <AnalyticsDashboard />;
      };

      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Analytics Dashboard')).toBeInTheDocument();
      });

      // Should not have excessive renders
      expect(renderSpy).toHaveBeenCalledTimes(1);
    });

    it('handles concurrent API calls gracefully', async () => {
      let callCount = 0;
      server.use(
        http.get('/api/initial-data', async () => {
          callCount++;
          await new Promise(resolve => setTimeout(resolve, 100));
          return HttpResponse.json({
            user: { username: 'test_user' },
            channels: [],
            scheduled_posts: [],
            plan: { name: 'Test Plan' }
          });
        })
      );

      // Force store to use API data source before rendering
      setTestDataSource('api');

      render(
        <TestWrapper>
          <AnalyticsDashboard />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Analytics Dashboard')).toBeInTheDocument();
      });

      // Should not make duplicate API calls
      expect(callCount).toBe(1);
    });
  });
});
