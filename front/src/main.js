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
let swRegistration = null
registerSW({
  immediate: true,
  onRegisteredSW(_url, registration) {
    swRegistration = registration
  },
})

// iOS suspends an installed PWA's WKWebView in the background instead of
// reloading it, so main.js never re-runs (and the SW never re-checks for
// an update) just from reopening the app — only `pageshow` with
// `persisted: true` fires to signal this resume-from-suspend, as opposed
// to a fresh navigation. Forcing registration.update() here lets the
// existing autoUpdate/reload flow set up above take over if a new
// version is found (cf. issue #75).
window.addEventListener('pageshow', (event) => {
  if (event.persisted) swRegistration?.update()
})

createApp(App).use(createPinia()).use(router).mount('#app')
