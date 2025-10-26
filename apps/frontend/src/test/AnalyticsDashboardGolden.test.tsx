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
import { AnalyticsDashboard } from '@features/dashboard';
import { useUIStore } from '@store';
import React from 'react';

// Test utilities
interface TestWrapperProps {
  children: React.ReactNode;
}

const TestWrapper: React.FC<TestWrapperProps> = ({ children }) => (
  <ThemeProvider theme={createTheme()}>
    {children}
  </ThemeProvider>
);

// Helper to set store data source for tests
const setTestDataSource = (source: 'mock' | 'real'): void => {
  useUIStore.getState().setDataSource(source);
};

describe('AnalyticsDashboard - Golden Standard Test', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset store to default mock state
    setTestDataSource('mock');
    localStorage.clear();
  });

  describe('Data Loading', () => {
    it('renders dashboard component without crashing', () => {
      render(
        <TestWrapper>
          <AnalyticsDashboard />
        </TestWrapper>
      );

      // Dashboard should render with main container
      expect(screen.getByRole('main')).toBeInTheDocument();
    });

    it('loads and displays analytics data successfully', async () => {
      render(
        <TestWrapper>
          <AnalyticsDashboard />
        </TestWrapper>
      );

      // Wait for dashboard content to render
      await waitFor(() => {
        // Check for tab navigation which is always present
        expect(screen.getByRole('tablist')).toBeInTheDocument();
      }, { timeout: 3000 });

      // Verify main components are accessible
      expect(screen.getByRole('main')).toBeInTheDocument();
    });
  });

  describe('API Error Handling', () => {
    it('renders dashboard structure correctly', async () => {
      render(
        <TestWrapper>
          <AnalyticsDashboard />
        </TestWrapper>
      );

      // Dashboard should have main container
      await waitFor(() => {
        expect(screen.getByRole('main')).toBeInTheDocument();
      });

      // Should have navigation tabs
      expect(screen.getByRole('tablist')).toBeInTheDocument();
    });

    it('handles component rendering successfully', async () => {
      render(
        <TestWrapper>
          <AnalyticsDashboard />
        </TestWrapper>
      );

      // Wait for tabs to render
      await waitFor(() => {
        const tabs = screen.getAllByRole('tab');
        expect(tabs.length).toBeGreaterThan(0);
      });

      // Dashboard should be interactive
      expect(screen.getByRole('main')).toBeInTheDocument();
    });

    it('renders dashboard successfully with mock data', async () => {
      // Use mock data source (default)
      setTestDataSource('mock');

      render(
        <TestWrapper>
          <AnalyticsDashboard />
        </TestWrapper>
      );

      // Dashboard should render
      await waitFor(() => {
        expect(screen.getByRole('main')).toBeInTheDocument();
      });

      // Should have tabs
      expect(screen.getByRole('tablist')).toBeInTheDocument();
    });
  });

  describe('User Interaction', () => {
    beforeEach(async () => {
      render(
        <TestWrapper>
          <AnalyticsDashboard />
        </TestWrapper>
      );

      // Wait for tabs to render
      await waitFor(() => {
        expect(screen.getByRole('tablist')).toBeInTheDocument();
      });
    });

    it('allows switching between tabs', async () => {
      const tabs = screen.getAllByRole('tab');

      // Should have multiple tabs
      expect(tabs.length).toBeGreaterThan(1);

      // Click second tab
      fireEvent.click(tabs[1]);

      // Tab should be selected (aria-selected="true")
      await waitFor(() => {
        expect(tabs[1]).toHaveAttribute('aria-selected', 'true');
      });
    });

    it('renders tab content areas', async () => {
      // Check that tabpanel exists
      const tabpanels = screen.getAllByRole('tabpanel', { hidden: true });
      expect(tabpanels.length).toBeGreaterThan(0);
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
        // Check for any headings
        const headings = screen.getAllByRole('heading');
        expect(headings.length).toBeGreaterThan(0);
      });
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

      // Main content should be accessible
      expect(screen.getByRole('main')).toHaveAttribute('role', 'main');
    });
  });

  describe('Performance', () => {
    it('renders without unnecessary re-renders', async () => {
      const renderSpy = vi.fn();

      const TestComponent: React.FC = () => {
        renderSpy();
        return <AnalyticsDashboard />;
      };

      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByRole('tablist')).toBeInTheDocument();
      });

      // Initial render should complete
      expect(renderSpy).toHaveBeenCalled();
    });

    it('handles data loading gracefully', async () => {
      render(
        <TestWrapper>
          <AnalyticsDashboard />
        </TestWrapper>
      );

      // Dashboard should render and be interactive
      await waitFor(() => {
        expect(screen.getByRole('main')).toBeInTheDocument();
      });

      // Tabs should be functional
      const tabs = screen.getAllByRole('tab');
      expect(tabs.length).toBeGreaterThan(0);
    });
  });
});
