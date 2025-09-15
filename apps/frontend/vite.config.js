import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react({
      // Use standard React JSX runtime for better compatibility
      jsxRuntime: 'automatic',
      jsxImportSource: 'react'
    })
  ],
  
  // Environment variable prefix
  envPrefix: ['VITE_', 'REACT_APP_'],
  
  // Build optimizations
  build: {
    // Target modern browsers for smaller bundles
    target: 'es2020',
    
    // Enable minification with advanced options
    minify: 'terser',
    
    // Terser options for better compression
    terserOptions: {
      compress: {
        drop_console: true, // Always drop console in production builds
        drop_debugger: true, // Always drop debugger in production builds
        pure_funcs: ['console.log', 'console.info'] // Remove specific console methods
      }
    },
    
    // Optimize chunks with advanced splitting
    rollupOptions: {
      external: (id) => {
        // Don't externalize anything - keep everything bundled
        return false;
      },
      output: {
        manualChunks(id) {
          // Core React ecosystem
          if (id.includes('node_modules/react') || id.includes('node_modules/@types/react')) {
            return 'react-core';
          }
          
          // React Router
          if (id.includes('react-router')) {
            return 'react-router';
          }
          
          // MUI Core Components
          if (id.includes('@mui/material') && !id.includes('icons')) {
            return 'mui-core';
          }
          
          // MUI Icons - ensure React is available
          if (id.includes('@mui/icons-material')) {
            return 'mui-icons';
          }
          
          // Emotion styling
          if (id.includes('@emotion')) {
            return 'emotion';
          }
          
          // Charts library
          if (id.includes('recharts')) {
            return 'charts-vendor';
          }
          
          // Analytics components (app-specific)
          if (id.includes('/components/analytics/') || id.includes('/components/dashboard/')) {
            return 'analytics-app';
          }
          
          // Admin components
          if (id.includes('/components/domains/admin/') || id.includes('/components/SuperAdmin')) {
            return 'admin-app';
          }
          
          // Services components  
          if (id.includes('/services/') && id.includes('Service')) {
            return 'services-app';
          }
          
          // Utilities and shared code
          if (id.includes('/utils/') || id.includes('/hooks/') || id.includes('/store/')) {
            return 'shared-utils';
          }
          
          // Common components
          if (id.includes('/components/common/')) {
            return 'common-components';
          }
          
          // All other vendor dependencies
          if (id.includes('node_modules')) {
            return 'vendor-misc';
          }
        },
        // Clean chunk names
        chunkFileNames: 'js/[name]-[hash].js',
        entryFileNames: 'js/[name]-[hash].js',
        assetFileNames: (assetInfo) => {
          const extType = assetInfo.name.split('.').at(1);
          if (/png|jpe?g|svg|gif|tiff|bmp|ico/i.test(extType)) {
            return `images/[name]-[hash][extname]`;
          }
          if (/css/i.test(extType)) {
            return `css/[name]-[hash][extname]`;
          }
          return `assets/[name]-[hash][extname]`;
        }
      },
      // Enhanced tree shaking
      treeshake: {
        preset: 'recommended',
        moduleSideEffects: false,
        propertyReadSideEffects: false,
        tryCatchDeoptimization: false
      }
    },
    
    // Source maps - disable in production to avoid dev file references
    sourcemap: process.env.NODE_ENV === 'development',
    
    // Optimize assets with better thresholds
    assetsInlineLimit: 8192, // 8kb - inline small assets
    
    // Chunk size warnings
    chunkSizeWarningLimit: 1000, // 1MB warning threshold
    
    // CSS code splitting
    cssCodeSplit: true
  },
  
  // Development optimizations
  server: {
    // Fast refresh
    hmr: true,
    // CORS for development
    cors: true,
    // Port configuration - use environment variable or default
    port: parseInt(process.env.VITE_PORT) || 5173,
    host: '0.0.0.0', // Allow external connections
    // Watch options for better file watching in Docker
    watch: {
      usePolling: true,
      interval: 100
    }
  },
  
  // Path resolution
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@components': resolve(__dirname, 'src/components'),
      '@utils': resolve(__dirname, 'src/utils'),
      '@store': resolve(__dirname, 'src/store'),
      '@hooks': resolve(__dirname, 'src/hooks')
    }
  },
  
  // Environment variables
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version || '1.0.0'),
    // Define process.env for browser compatibility
    'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV || 'development'),
    'process.env.REACT_APP_API_BASE_URL': JSON.stringify(process.env.REACT_APP_API_BASE_URL || process.env.VITE_API_URL || 'http://localhost:8000'),
    'process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY': JSON.stringify(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY || process.env.VITE_STRIPE_PUBLISHABLE_KEY || ''),
    // Ensure React is available globally for JSX runtime
    'global': 'globalThis',
  },
  
  // Performance optimizations
  esbuild: {
    // Tree shaking for better bundle size
    treeShaking: true,
    // Keep console logs in development for debugging
    drop: []
  },

  // Dependency optimization
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react/jsx-runtime',
      'react/jsx-dev-runtime',
      '@mui/material',
      '@mui/icons-material',
      '@emotion/react',
      '@emotion/styled'
    ],
    force: true
  }
})
