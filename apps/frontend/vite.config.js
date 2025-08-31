import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  
  // Build optimizations
  build: {
    // Target modern browsers for smaller bundles
    target: 'es2020',
    
    // Enable minification
    minify: 'terser',
    
    // Optimize chunks
    rollupOptions: {
      output: {
        manualChunks: {
          // Vendor chunks for better caching
          'react-vendor': ['react', 'react-dom'],
          'mui-vendor': [
            '@mui/material',
            '@mui/icons-material'
          ],
          'utils': [
            './src/utils/apiClient.js',
            './src/utils/errorHandler.js'
          ]
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
      }
    },
    
    // Source maps for debugging
    sourcemap: process.env.NODE_ENV !== 'production',
    
    // Optimize assets
    assetsInlineLimit: 4096, // 4kb
  },
  
  // Development optimizations
  server: {
    // Fast refresh
    hmr: true,
    // CORS for development
    cors: true,
    // Port configuration
    port: 3000,
    host: true
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
