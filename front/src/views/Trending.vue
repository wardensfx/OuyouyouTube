<script setup>
import { computed, onMounted, ref } from 'vue'
import { ArrowLeft } from '@lucide/vue'
import { api } from '../api/client'
import { useProgressStore } from '../stores/progress'
import { usePaginatedList } from '../composables/usePaginatedList'
import { useInfiniteScroll } from '../composables/useInfiniteScroll'
import VideoCard from '../components/VideoCard.vue'
import AddToPlaylistModal from '../components/AddToPlaylistModal.vue'
import SkeletonCard from '../components/SkeletonCard.vue'
import EmptyState from '../components/EmptyState.vue'
import LoadMoreStatus from '../components/LoadMoreStatus.vue'

defineOptions({ name: 'Trending' })
const SKELETON_COUNT = 6

const progressStore = useProgressStore()
const {
  items: videos,
  loading,
  loadingMore,
  error,
  loadMoreError,
  nextPageToken,
  load,
  loadMore,
} = usePaginatedList((pageToken) => api.getTrending(pageToken))
// Vidéo déjà vue = hors du flux de découverte (contrairement aux
// Favoris/Playlists, qu'on constitue soi-même).
const visibleVideos = computed(() => videos.value.filter((v) => !progressStore.items[v.video_id]?.watched))
const modalVideo = ref(null)

async function loadWithProgress() {
  progressStore.fetchFor((await load()).map((v) => v.video_id))
}
async function loadMoreWithProgress() {
  progressStore.fetchFor((await loadMore()).map((v) => v.video_id))
}
const { sentinel } = useInfiniteScroll(loadMoreWithProgress)

onMounted(loadWithProgress)
</script>

<template>
  <div class="page">
    <RouterLink to="/" class="back"><ArrowLeft :size="16" /> Retour</RouterLink>
    <h1>Tendances</h1>

    <div v-if="loading" class="grid">
      <SkeletonCard v-for="n in SKELETON_COUNT" :key="n" />
    </div>
    <div v-else-if="error" class="state state--error">
      <p>{{ error }}</p>
      <button class="retry-btn" @click="loadWithProgress">Réessayer</button>
    </div>
    <EmptyState v-else-if="!visibleVideos.length" message="Rien à afficher pour l'instant." />

    <template v-else>
      <div class="grid">
        <VideoCard
          v-for="v in visibleVideos"
          :key="v.video_id"
          :video="v"
          @add-to-playlist="modalVideo = v"
        />
      </div>
      <div v-if="nextPageToken" ref="sentinel" class="sentinel" />
      <LoadMoreStatus :loading="loadingMore" :error="loadMoreError" @retry="loadMoreWithProgress" />
    </template>

    <AddToPlaylistModal v-if="modalVideo" :video="modalVideo" @close="modalVideo = null" />
  </div>
</template>

<style scoped>
.page {
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
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.5rem;
}
.retry-btn {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-pill);
  color: inherit;
  padding: 0.4rem 0.9rem;
  font-size: 0.85rem;
  cursor: pointer;
}
.sentinel {
  height: 1px;
}
.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}
</style>
