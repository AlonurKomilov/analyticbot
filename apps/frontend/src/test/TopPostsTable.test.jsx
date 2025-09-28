import { render, screen, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import TopPostsTable from '../components/analytics/TopPostsTable/TopPostsTable';

const theme = createTheme();

const TestWrapper = ({ children }) => (
  <ThemeProvider theme={theme}>
    {children}
  </ThemeProvider>
);

// Mock data
const mockTopPostsData = {
  posts: [
    {
      id: 1,
      title: "Amazing Post About AI",
      content: "This is an amazing post about artificial intelligence...",
      author: {
        name: "John Smith",
        avatar: "https://i.pravatar.cc/40?img=1"
      },
      publishedAt: "2024-01-15T10:00:00Z",
      metrics: {
        views: 15420,
        likes: 892,
        comments: 134,
        shares: 67,
        engagement: 7.8
      },
      tags: ["AI", "Technology", "Future"]
    },
    {
      id: 2,
      title: "Machine Learning Insights",
      content: "Deep dive into machine learning algorithms...",
      author: {
        name: "Sarah Johnson",
        avatar: "https://i.pravatar.cc/40?img=2"
      },
      publishedAt: "2024-01-14T14:30:00Z",
      metrics: {
        views: 12350,
        likes: 743,
        comments: 89,
        shares: 45,
        engagement: 7.1
      },
      tags: ["ML", "Data Science"]
    },
    {
      id: 3,
      title: "Data Science Tips",
      content: "Essential tips for data scientists...",
      author: {
        name: "Mike Chen",
        avatar: "https://i.pravatar.cc/40?img=3"
      },
      publishedAt: "2024-01-13T09:15:00Z",
      metrics: {
        views: 9876,
        likes: 567,
        comments: 78,
        shares: 34,
        engagement: 6.8
      },
      tags: ["Data Science", "Tips"]
    }
  ]
};

describe('TopPostsTable', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Mock fetch API
    window.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockTopPostsData),
      })
    );
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders table title correctly', () => {
    render(
      <TestWrapper>
        <TopPostsTable />
      </TestWrapper>
    );

    expect(screen.getByText('Top Performing Posts')).toBeInTheDocument();
  });

  it('shows loading state initially', () => {
    render(
      <TestWrapper>
        <TopPostsTable />
      </TestWrapper>
    );

    expect(screen.getByText('Loading top posts...')).toBeInTheDocument();
  });

  it('renders filter controls', () => {
    render(
      <TestWrapper>
        <TopPostsTable />
      </TestWrapper>
    );

    expect(screen.getAllByText('Time Period')).toHaveLength(2); // label and legend
    expect(screen.getAllByText('Sort By')).toHaveLength(2); // label and legend
  });

  it('displays table headers correctly', async () => {
    render(
      <TestWrapper>
        <TopPostsTable />
      </TestWrapper>
    );

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Post Content')).toBeInTheDocument();
    });

    expect(screen.getByRole('columnheader', { name: /views/i })).toBeInTheDocument();
    expect(screen.getByRole('columnheader', { name: /likes/i })).toBeInTheDocument();
    expect(screen.getByRole('columnheader', { name: /comments/i })).toBeInTheDocument();
    expect(screen.getByRole('columnheader', { name: /engagement rate/i })).toBeInTheDocument();
  });

  it('displays post data correctly', async () => {
    render(
      <TestWrapper>
        <TopPostsTable />
      </TestWrapper>
    );

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText(/AI Analytics Dashboard/)).toBeInTheDocument();
    });

    expect(screen.getByText(/Weekly Performance Report/)).toBeInTheDocument();
    expect(screen.getByText(/Best Practices for Content/)).toBeInTheDocument();
  });
});
