<script setup>
import AccountSwitcher from './components/AccountSwitcher.vue'
</script>

<template>
  <div class="app">
    <header class="topbar">
      <RouterLink to="/" class="brand">OuyouyouTube</RouterLink>
      <div class="topbar__actions">
        <RouterLink to="/search" class="search-link" title="Rechercher">🔍</RouterLink>
        <AccountSwitcher />
      </div>
    </header>
    <main class="app__content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #222;
  position: sticky;
  top: 0;
  background: #0f0f0f;
  z-index: 10;
}
.brand {
  font-weight: 700;
  font-size: 1.05rem;
  color: inherit;
  text-decoration: none;
  letter-spacing: -0.02em;
}
.topbar__actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.search-link {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  color: inherit;
  text-decoration: none;
  font-size: 1rem;
}
.search-link:hover {
  background: #1f1f1f;
}
.app__content {
  flex: 1;
}
</style>
