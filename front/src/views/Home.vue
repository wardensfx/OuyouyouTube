<script setup>
import { onMounted } from 'vue'
import { useLibraryStore } from '../stores/library'
import VideoCard from '../components/VideoCard.vue'
import PlaylistCard from '../components/PlaylistCard.vue'

const library = useLibraryStore()
onMounted(() => library.loadAll())
</script>

<template>
  <div class="home">
    <header class="home__header">
      <h1>Ma bibliothèque</h1>
    </header>

    <p v-if="library.loading" class="state">Chargement…</p>
    <p v-else-if="library.error" class="state state--error">{{ library.error }}</p>

    <template v-else>
      <section class="section">
        <h2>Playlists</h2>
        <div class="grid">
          <PlaylistCard v-for="p in library.playlists" :key="p.id" :playlist="p" />
        </div>
      </section>

      <section class="section">
        <h2>Favoris</h2>
        <div class="grid">
          <VideoCard v-for="v in library.favorites" :key="v.video_id" :video="v" />
        </div>
      </section>
    </template>
  </div>
</template>

<style scoped>
.home__header {
  padding: 1rem;
}
.section {
  padding: 0 1rem 1.5rem;
}
.section h2 {
  font-size: 1rem;
  opacity: 0.7;
  margin-bottom: 0.75rem;
}
.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}
.state {
  padding: 1rem;
  opacity: 0.7;
}
.state--error {
  color: #ff6b6b;
}
</style>
