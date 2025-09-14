import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react({
      // React performance optimizations
      jsxImportSource: '@emotion/react'
    })
  ],
  
  // Build optimizations
  build: {
    // Target modern browsers for smaller bundles
    target: 'es2020',
    
    // Enable minification with advanced options
    minify: 'terser',
    
    // Terser options for better compression
    terserOptions: {
      compress: {
        drop_console: process.env.NODE_ENV === 'production',
        drop_debugger: process.env.NODE_ENV === 'production',
        pure_funcs: process.env.NODE_ENV === 'production' ? ['console.log', 'console.info'] : []
      }
    },
    
    // Optimize chunks with advanced splitting
    rollupOptions: {
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
          
          // MUI Core Components (split into smaller chunks)
          if (id.includes('@mui/material') && !id.includes('icons')) {
            return 'mui-core';
          }
          
          // MUI Icons (separate chunk - lazy loaded)
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
    
    // Source maps for debugging
    sourcemap: process.env.NODE_ENV !== 'production',
    
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
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
  },
  
  // Performance optimizations
  esbuild: {
    // Tree shaking for better bundle size
    treeShaking: true,
    // Drop console logs in production
    ...(process.env.NODE_ENV === 'production' && {
      drop: ['console', 'debugger']
    })
  }
})
