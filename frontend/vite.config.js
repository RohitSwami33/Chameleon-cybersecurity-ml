import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5174,
<<<<<<< HEAD
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
=======
    strictPort: false,   // fallback to 5175 if 5174 is taken
    host: true,
    proxy: {
      // All backend API calls
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      // /trap/execute and other /trap/* endpoints (no /api prefix in backend)
      '/trap': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
>>>>>>> 5035a73d50efbedccaead6fb1e12408899a269ef
    }
  },
  preview: {
    port: process.env.PORT || 4173,
    host: '0.0.0.0'
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    emptyOutDir: true
  }
})
<<<<<<< HEAD
=======

>>>>>>> 5035a73d50efbedccaead6fb1e12408899a269ef
