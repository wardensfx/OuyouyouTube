<script setup>
import { onMounted } from 'vue'
import { useLibraryStore } from '../stores/library'

const library = useLibraryStore()
onMounted(() => {
  if (!library.playlists.length) library.loadAll()
})
</script>

<template>
  <aside class="sidebar glass">
    <nav class="sidebar__nav">
      <RouterLink to="/" class="sidebar__link" active-class="sidebar__link--active" exact>
        <span class="sidebar__icon">🏠</span> Accueil
      </RouterLink>
      <RouterLink to="/search" class="sidebar__link" active-class="sidebar__link--active">
        <span class="sidebar__icon">🔍</span> Recherche
      </RouterLink>
    </nav>

    <div class="sidebar__section">
      <h3 class="sidebar__title">Playlists</h3>
      <RouterLink
        v-for="p in library.playlists"
        :key="p.id"
        :to="{ name: 'playlist', params: { id: p.id } }"
        class="sidebar__link sidebar__link--playlist"
        active-class="sidebar__link--active"
      >
        {{ p.title }}
      </RouterLink>
      <p v-if="!library.playlists.length" class="sidebar__empty">Aucune playlist pour l'instant.</p>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 240px;
  flex-shrink: 0;
  padding: 1rem 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  overflow-y: auto;
}
.sidebar__nav {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}
.sidebar__link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 0.75rem;
  border-radius: var(--radius-md);
  color: var(--text);
  text-decoration: none;
  font-size: 0.9rem;
  transition: background 0.15s ease;
}
.sidebar__link:hover {
  background: rgba(255, 255, 255, 0.08);
}
.sidebar__link--active {
  background: rgba(255, 255, 255, 0.12);
  font-weight: 600;
}
.sidebar__icon {
  font-size: 1.05rem;
}
.sidebar__link--playlist {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: block;
}
.sidebar__section {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}
.sidebar__title {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-dim);
  margin: 0 0.75rem 0.5rem;
}
.sidebar__empty {
  font-size: 0.8rem;
  color: var(--text-dim);
  margin: 0 0.75rem;
}

@media (max-width: 768px) {
  .sidebar {
    display: none;
  }
}
</style>
