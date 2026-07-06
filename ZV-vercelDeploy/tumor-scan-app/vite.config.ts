import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 8080,
    cors: true,
    headers: {
      'Access-Control-Allow-Origin': '*',
    },
    proxy: {
      // String shorthand: http://localhost:5173/api -> http://localhost:8080/api
      '/api': {
        target: 'http://localhost', //backend URL
        changeOrigin: true,
        secure: false,
      },
    }
  },
})
