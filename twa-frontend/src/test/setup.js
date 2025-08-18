import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock Telegram Web App
global.Telegram = {
  WebApp: {
    ready: vi.fn(),
    expand: vi.fn(),
    initData: 'mock-init-data',
    initDataUnsafe: {
      user: {
        id: 123456,
        first_name: 'Test',
        last_name: 'User',
        username: 'testuser'
      }
    },
    colorScheme: 'dark',
    showAlert: vi.fn(),
    showConfirm: vi.fn(),
    HapticFeedback: {
      impactOccurred: vi.fn(),
      notificationOccurred: vi.fn()
    }
  }
};

// Mock environment variables
vi.mock('import.meta', () => ({
  env: {
    VITE_API_URL: 'http://localhost:3001',
    VITE_ENVIRONMENT: 'test'
  }
}));

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn(() => ({
  observe: vi.fn(),
  disconnect: vi.fn(),
  unobserve: vi.fn()
}));

// Mock ResizeObserver
global.ResizeObserver = vi.fn(() => ({
  observe: vi.fn(),
  disconnect: vi.fn(),
  unobserve: vi.fn()
}));

// Mock URL.createObjectURL
global.URL.createObjectURL = vi.fn(() => 'mock-object-url');
global.URL.revokeObjectURL = vi.fn();

// Mock fetch for API tests
global.fetch = vi.fn();

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
};
global.localStorage = localStorageMock;

// Mock sessionStorage
const sessionStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
};
global.sessionStorage = sessionStorageMock;
