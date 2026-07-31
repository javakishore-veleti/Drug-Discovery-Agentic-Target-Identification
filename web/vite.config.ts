import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // AWS SDK / Amplify (aws mode) sometimes reference Node `process` in the browser.
  define: {
    'process.env': {},
  },
})
