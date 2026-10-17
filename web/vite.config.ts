import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  // MapLibre's worker is bundled separately (see src/components/map/maplibreWorker.ts).
  worker: { format: 'es' },
  // Local contribution backend: python -m croptransfer.contrib_server (port 8787).
  server: { port: 5180, strictPort: true, proxy: { '/api': 'http://127.0.0.1:8787' } },
  preview: { port: 5181, strictPort: true },
  build: {
    chunkSizeWarningLimit: 1200,
    rolldownOptions: {
      output: {
        advancedChunks: {
          groups: [
            { name: 'maplibre', test: /maplibre-gl|terra-draw/ },
            { name: 'react', test: /node_modules[\/](react|react-dom|react-router|scheduler)[\/]/ },
          ],
        },
      },
    },
  },
})
