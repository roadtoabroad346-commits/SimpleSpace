import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

// GitHub Pages serves this project below /SimpleSpace/.
// VITE_BASE_PATH can override the path for other hosting providers.
export default defineConfig({
  base: process.env.VITE_BASE_PATH || '/SimpleSpace/',
  plugins: [react(), tailwindcss()],
  test: {
    environment: 'jsdom',
    setupFiles: './src/test-setup.ts',
    globals: true,
  },
})
