import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// Owner Panel Vite Configuration
export default defineConfig({
  plugins: [
    react({
      jsxRuntime: 'automatic',
      jsxImportSource: 'react'
    }),
  ],

  // Environment variable prefix
  envPrefix: ['VITE_'],

  // Build optimizations
  build: {
    target: 'es2020',
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      }
    },
    outDir: 'dist',
    sourcemap: false,
  },

  // Development server
  server: {
    port: 11340,
    host: '0.0.0.0',
    cors: true,
    hmr: true,
    allowedHosts: [
      'owner.analyticbot.org',
      'localhost',
      '127.0.0.1',
    ],
    proxy: {
      // Proxy API requests to backend
      '/api': {
        target: 'http://localhost:11400',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
        secure: false,
      },
    },
  },

  // Preview server
  preview: {
    port: 11340,
    host: '0.0.0.0',
  },

  // Path aliases
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
      '@components': resolve(__dirname, './src/components'),
      '@pages': resolve(__dirname, './src/pages'),
      '@hooks': resolve(__dirname, './src/hooks'),
      '@api': resolve(__dirname, './src/api'),
      '@utils': resolve(__dirname, './src/utils'),
      '@config': resolve(__dirname, './src/config'),
      '@contexts': resolve(__dirname, './src/contexts'),
      '@layouts': resolve(__dirname, './src/layouts'),
      '@theme': resolve(__dirname, './src/theme'),
    },
  },

  // Dependency optimization
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-router-dom', '@mui/material', '@emotion/react', '@emotion/styled'],
    exclude: [],
  },
})
