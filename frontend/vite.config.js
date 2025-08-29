import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          // Vendor chunks
          if (id.includes('node_modules')) {
            if (id.includes('react') || id.includes('react-dom')) {
              return 'react-vendor'
            }
            if (id.includes('recharts')) {
              return 'chart-vendor'
            }
            if (id.includes('axios')) {
              return 'http-vendor'
            }
            // Other vendor libraries
            return 'vendor'
          }

          // App chunks
          if (id.includes('/src/components/')) {
            return 'components'
          }
          if (id.includes('/src/hooks/') || id.includes('/src/utils/')) {
            return 'utils'
          }
          if (id.includes('/src/services/')) {
            return 'services'
          }
        }
      }
    },
    // Increase chunk size warning limit to 1000kb (from default 500kb)
    chunkSizeWarningLimit: 1000,
    // Enable source maps for production debugging
    sourcemap: false,
    // Optimize for production
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // Remove console.logs in production
        drop_debugger: true
      }
    }
  },
  // Optimize dev server
  server: {
    port: 3000,
    open: true
  }
})
