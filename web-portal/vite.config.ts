import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Exposes the server to the network
    port: 5173,      // This is the default port, you can change it if needed
    watch: {
      usePolling: true, // Helps with file change detection in some Docker setups
    },
  }
})
