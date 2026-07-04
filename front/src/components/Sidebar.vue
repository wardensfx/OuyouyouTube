<script setup>
import { onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Home, Search, Rss, TrendingUp, Heart, Settings2 } from '@lucide/vue'
import { useLibraryStore } from '../stores/library'
import { usePlaylistOrder } from '../composables/usePlaylistOrder'

const props = defineProps({ open: { type: Boolean, default: false } })
const emit = defineEmits(['close'])

const library = useLibraryStore()
onMounted(() => {
  if (!library.playlists.length) library.loadAll()
})

const { ordered } = usePlaylistOrder(() => library.playlists)

const route = useRoute()
watch(() => route.fullPath, () => emit('close'))
</script>

<template>
  <div v-if="open" class="sidebar__backdrop" @click="emit('close')" />
  <aside class="sidebar glass" :class="{ 'sidebar--open': open }">
    <nav class="sidebar__nav">
      <RouterLink to="/" class="sidebar__link" active-class="sidebar__link--active" exact>
        <Home :size="18" /> Accueil
      </RouterLink>
      <RouterLink to="/search" class="sidebar__link" active-class="sidebar__link--active">
        <Search :size="18" /> Recherche
      </RouterLink>
      <RouterLink to="/subscriptions" class="sidebar__link" active-class="sidebar__link--active">
        <Rss :size="18" /> Abonnements
      </RouterLink>
      <RouterLink to="/trending" class="sidebar__link" active-class="sidebar__link--active">
        <TrendingUp :size="18" /> Tendances
      </RouterLink>
      <RouterLink to="/favorites" class="sidebar__link" active-class="sidebar__link--active">
        <Heart :size="18" /> Vidéos aimées
      </RouterLink>
    </nav>

    <div class="sidebar__section">
      <div class="sidebar__section-header">
        <h3 class="sidebar__title">Playlists</h3>
        <RouterLink to="/playlists/manage" class="sidebar__manage" title="Gérer les playlists">
          <Settings2 :size="14" />
        </RouterLink>
      </div>
      <RouterLink
        v-for="p in ordered"
        :key="p.id"
        :to="{ name: 'playlist', params: { id: p.id } }"
        class="sidebar__link sidebar__link--playlist"
        active-class="sidebar__link--active"
      >
        {{ p.title }}
      </RouterLink>
      <p v-if="!ordered.length" class="sidebar__empty">Aucune playlist pour l'instant.</p>
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
  position: sticky;
  top: 0;
  height: 100vh;
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
.sidebar__section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 0 0.75rem 0.5rem;
}
.sidebar__title {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-dim);
  margin: 0;
}
.sidebar__manage {
  color: var(--text-dim);
  display: flex;
}
.sidebar__manage:hover {
  color: var(--text);
}
.sidebar__empty {
  font-size: 0.8rem;
  color: var(--text-dim);
  margin: 0 0.75rem;
}

@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    height: 100vh;
    z-index: 41;
    transform: translateX(-100%);
    transition: transform 0.25s ease;
    border-radius: 0;
  }
  .sidebar--open {
    transform: translateX(0);
  }
  .sidebar__backdrop {
    position: fixed;
    inset: 0;
    z-index: 40;
    background: rgba(0, 0, 0, 0.5);
  }
}
</style>
