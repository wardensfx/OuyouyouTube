<script setup>
import AccountSwitcher from './components/AccountSwitcher.vue'
import Sidebar from './components/Sidebar.vue'
import BottomNav from './components/BottomNav.vue'
</script>

<template>
  <div class="app">
    <Sidebar />

    <div class="app__main">
      <header class="topbar glass">
        <RouterLink to="/" class="brand">OuyouyouTube</RouterLink>
        <AccountSwitcher />
      </header>

      <main class="app__content">
        <RouterView v-slot="{ Component }">
          <KeepAlive :include="['Home', 'Search', 'PlaylistDetail']">
            <component :is="Component" />
          </KeepAlive>
        </RouterView>
      </main>
    </div>

    <BottomNav />
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
}
.app__main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1.25rem;
  position: sticky;
  top: 0;
  z-index: 10;
  border-radius: 0;
  border-top: none;
  border-left: none;
  border-right: none;
}
.brand {
  font-weight: 700;
  font-size: 1.05rem;
  color: inherit;
  text-decoration: none;
  letter-spacing: -0.02em;
}
.app__content {
  flex: 1;
  padding-bottom: env(safe-area-inset-bottom);
}

@media (max-width: 768px) {
  .app__content {
    padding-bottom: calc(4rem + env(safe-area-inset-bottom));
  }
}
</style>
