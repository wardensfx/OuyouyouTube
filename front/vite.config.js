import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.svg', 'icons/*.png'],
      manifest: {
        name: 'YT Stream',
        short_name: 'YTStream',
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
        // On ne cache jamais les vidéos ni les appels API dynamiques (auth/cookies)
        navigateFallbackDenylist: [/^\/api/, /^\/auth/, /^\/video/],
        runtimeCaching: [
          {
            urlPattern: ({ url }) => url.pathname.startsWith('/playlists') || url.pathname.startsWith('/favorites'),
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
      '/auth': 'http://127.0.0.1:8000',
      '/playlists': 'http://127.0.0.1:8000',
      '/favorites': 'http://127.0.0.1:8000',
      '/video': 'http://127.0.0.1:8000',
    },
  },
})
