import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  define: {
    // Injected at build time — set VITE_API_URL in Vercel env vars
    __API_URL__: JSON.stringify(process.env.VITE_API_URL ?? ''),
  },
})
