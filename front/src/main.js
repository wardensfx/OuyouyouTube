import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { registerSW } from 'virtual:pwa-register'
import App from './App.vue'
import { router } from './router'
import './style.css'

// vite.config.js's registerType: 'autoUpdate' makes Workbox skip-waiting
// and claim clients on a new deploy, but that alone never reloads an
// already-open tab/installed PWA — without this call, the only way to
// actually see a new deploy was a hard refresh (clearing the cache),
// which also breaks an installed PWA out of standalone mode.
registerSW({ immediate: true })

createApp(App).use(createPinia()).use(router).mount('#app')
