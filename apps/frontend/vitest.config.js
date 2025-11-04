import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    // Use jsdom for DOM testing
    environment: 'jsdom',

    // Setup files
    setupFiles: ['./src/test/setup.js'],

    // Coverage configuration
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'json-summary'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.test.{js,jsx,ts,tsx}',
        '**/*.spec.{js,jsx,ts,tsx}',
        '**/dist/',
        'vite.config.js'
      ],
      thresholds: {
        global: {
          statements: 80,
          branches: 80,
          functions: 80,
          lines: 80
        }
      }
    },

    // Global test configuration
    globals: true,

    // Test file patterns
    include: ['src/**/*.{test,spec}.{js,jsx,ts,tsx}'],

    // Mock configuration
    mockReset: true,
    restoreMocks: true
  },

  // Path resolution (same as main vite config)
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
      '@features': resolve(__dirname, './src/features'),
      '@shared': resolve(__dirname, './src/shared'),
      '@store': resolve(__dirname, './src/store'),
      '@config': resolve(__dirname, './src/config'),
      '@theme': resolve(__dirname, './src/theme'),
      '@api': resolve(__dirname, './src/api'),
      '@pages': resolve(__dirname, './src/pages'),
      '@types': resolve(__dirname, './src/types'),
    }
  }
});
