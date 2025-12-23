import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// Public Catalog Vite Configuration
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
    port: 11320,
    host: '0.0.0.0',
    cors: true,
    hmr: true,
    allowedHosts: [
      'analyticbot.org',
      'www.analyticbot.org',
      'localhost',
      '127.0.0.1',
    ],
    proxy: {
      // Proxy API requests to backend
      '/api': {
        target: 'http://127.0.0.1:11400',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
        secure: false,
      },
      // Proxy public endpoints
      '/public': {
        target: 'http://127.0.0.1:11400',
        changeOrigin: true,
        secure: false,
      },
    },
  },

  // Path resolution
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@components': resolve(__dirname, 'src/components'),
      '@pages': resolve(__dirname, 'src/pages'),
      '@hooks': resolve(__dirname, 'src/hooks'),
      '@api': resolve(__dirname, 'src/api'),
      '@config': resolve(__dirname, 'src/config'),
      '@contexts': resolve(__dirname, 'src/contexts'),
      '@layouts': resolve(__dirname, 'src/layouts'),
      '@theme': resolve(__dirname, 'src/theme'),
    },
  },

  // Preview server
  preview: {
    port: 11320,
    host: '0.0.0.0',
  },
})
