import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// Moderator Panel Vite Configuration
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
    port: 11330,
    host: '0.0.0.0',
    cors: true,
    hmr: true,
    allowedHosts: [
      'moderator.analyticbot.org',
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
      // Proxy moderator endpoints
      '/moderator': {
        target: 'http://127.0.0.1:11400',
        changeOrigin: true,
        secure: false,
      },
      // Proxy public endpoints for category lists etc
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
      '@': resolve(__dirname, './src'),
      '@components': resolve(__dirname, './src/components'),
      '@pages': resolve(__dirname, './src/pages'),
      '@api': resolve(__dirname, './src/api'),
      '@config': resolve(__dirname, './src/config'),
      '@hooks': resolve(__dirname, './src/hooks'),
      '@contexts': resolve(__dirname, './src/contexts'),
      '@theme': resolve(__dirname, './src/theme'),
      '@utils': resolve(__dirname, './src/utils'),
    }
  },

  // Environment variables
  define: {
    __APP_VERSION__: JSON.stringify('1.0.0'),
    'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV || 'development'),
  },

  // Dependency optimization
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react/jsx-runtime',
      '@mui/material',
      '@mui/icons-material',
      '@emotion/react',
      '@emotion/styled'
    ],
  }
})
