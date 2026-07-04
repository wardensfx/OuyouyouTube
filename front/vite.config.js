import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.png', 'icons/*.png'],
      manifest: {
        name: 'OuyouyouTube',
        short_name: 'OuyouyouTube',
        description: 'Client YouTube personnel — playlists, favoris, lecture streamée',
        theme_color: '#0f0f0f',
        background_color: '#0f0f0f',
        display: 'standalone',
        orientation: 'portrait',
        start_url: '/',
        icons: [
          { src: '/icons/icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: '/icons/icon-512.png', sizes: '512x512', type: 'image/png' },
          { src: '/icons/icon-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
        ],
      },
      workbox: {
        // On ne cache jamais les appels API dynamiques (auth/cookies/vidéo)
        navigateFallbackDenylist: [/^\/api/],
        runtimeCaching: [
          {
            urlPattern: ({ url }) =>
              url.pathname.startsWith('/api/playlists') ||
              url.pathname.startsWith('/api/favorites') ||
              url.pathname.startsWith('/api/search') ||
              url.pathname.startsWith('/api/home'),
            handler: 'NetworkFirst',
            options: { cacheName: 'metadata-cache', expiration: { maxAgeSeconds: 60 * 10 } },
          },
        ],
      },
    }),
  ],
  server: {
    host: true,
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
})
