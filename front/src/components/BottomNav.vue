<script setup></script>

<template>
  <nav class="bottom-nav glass">
    <RouterLink to="/" class="bottom-nav__link" active-class="bottom-nav__link--active" exact>
      <span>🏠</span>
      <small>Accueil</small>
    </RouterLink>
    <RouterLink to="/search" class="bottom-nav__link" active-class="bottom-nav__link--active">
      <span>🔍</span>
      <small>Recherche</small>
    </RouterLink>
  </nav>
</template>

<style scoped>
.bottom-nav {
  display: none;
}

@media (max-width: 768px) {
  .bottom-nav {
    display: flex;
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    padding: 0.5rem 0.75rem calc(0.5rem + env(safe-area-inset-bottom));
    border-radius: 0;
    border-left: none;
    border-right: none;
    border-bottom: none;
    z-index: 15;
  }
}
.bottom-nav__link {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.15rem;
  color: var(--text-dim);
  text-decoration: none;
  font-size: 1.1rem;
  padding: 0.25rem;
  border-radius: var(--radius-md);
}
.bottom-nav__link small {
  font-size: 0.65rem;
}
.bottom-nav__link--active {
  color: var(--text);
}
</style>
