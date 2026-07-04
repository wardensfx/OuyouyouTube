<script setup>
import { onMounted, ref } from 'vue'
import { ArrowLeft } from '@lucide/vue'
import { useLibraryStore } from '../stores/library'
import { useProgressStore } from '../stores/progress'
import VideoCard from '../components/VideoCard.vue'
import AddToPlaylistModal from '../components/AddToPlaylistModal.vue'

defineOptions({ name: 'Liked' })

const library = useLibraryStore()
const progressStore = useProgressStore()
onMounted(async () => {
  if (!library.favorites.length) await library.loadAll()
  progressStore.fetchFor(library.favorites.map((v) => v.video_id))
})

const modalVideo = ref(null)
</script>

<template>
  <div class="liked">
    <RouterLink to="/" class="back"><ArrowLeft :size="16" /> Retour</RouterLink>
    <h1>Vidéos aimées</h1>

    <p v-if="library.loading" class="state">Chargement…</p>
    <p v-else-if="library.error" class="state state--error">{{ library.error }}</p>
    <p v-else-if="!library.favorites.length" class="state">Aucune vidéo aimée pour l'instant.</p>

    <TransitionGroup v-else tag="div" name="grid" class="grid">
      <VideoCard
        v-for="v in library.favorites"
        :key="v.video_id"
        :video="v"
        @add-to-playlist="modalVideo = v"
      />
    </TransitionGroup>

    <AddToPlaylistModal v-if="modalVideo" :video="modalVideo" @close="modalVideo = null" />
  </div>
</template>

<style scoped>
.liked {
  padding: 1rem;
}
.back {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  margin-bottom: 1rem;
  color: inherit;
  opacity: 0.7;
  text-decoration: none;
}
h1 {
  margin-bottom: 1rem;
}
.state {
  opacity: 0.7;
}
.state--error {
  color: var(--danger);
}
.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  position: relative;
}
.grid-enter-active,
.grid-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}
.grid-enter-from,
.grid-leave-to {
  opacity: 0;
  transform: scale(0.9);
}
.grid-leave-active {
  position: absolute;
}
.grid-move {
  transition: transform 0.25s ease;
}
</style>
