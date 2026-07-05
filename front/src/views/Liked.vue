<script setup>
import { onMounted, ref } from 'vue'
import { ArrowLeft, Heart } from '@lucide/vue'
import { useLibraryStore } from '../stores/library'
import { useProgressStore } from '../stores/progress'
import { useInfiniteScroll } from '../composables/useInfiniteScroll'
import VideoCard from '../components/VideoCard.vue'
import AddToPlaylistModal from '../components/AddToPlaylistModal.vue'
import SkeletonCard from '../components/SkeletonCard.vue'
import EmptyState from '../components/EmptyState.vue'
import LoadMoreStatus from '../components/LoadMoreStatus.vue'

defineOptions({ name: 'Liked' })
const SKELETON_COUNT = 6

const library = useLibraryStore()
const progressStore = useProgressStore()
async function load() {
  await library.loadAll()
  progressStore.fetchFor(library.favorites.map((v) => v.video_id))
}
onMounted(() => {
  if (!library.favorites.length) load()
})

async function loadMore() {
  const newItems = await library.loadMoreFavorites()
  if (newItems.length) progressStore.fetchFor(newItems.map((v) => v.video_id))
}
const { sentinel } = useInfiniteScroll(loadMore)

const modalVideo = ref(null)
</script>

<template>
  <div class="liked">
    <RouterLink to="/" class="back"><ArrowLeft :size="16" /> Retour</RouterLink>
    <h1>Vidéos aimées</h1>

    <div v-if="library.loading" class="grid">
      <SkeletonCard v-for="n in SKELETON_COUNT" :key="n" />
    </div>
    <div v-else-if="library.error" class="state state--error">
      <p>{{ library.error }}</p>
      <button class="retry-btn" @click="load">Réessayer</button>
    </div>
    <EmptyState v-else-if="!library.favorites.length" :icon="Heart" message="Aucune vidéo aimée pour l'instant." />

    <template v-else>
      <TransitionGroup tag="div" name="grid" class="grid">
        <VideoCard
          v-for="v in library.favorites"
          :key="v.video_id"
          :video="v"
          show-like
          @add-to-playlist="modalVideo = v"
        />
      </TransitionGroup>
      <div v-if="library.favoritesNextPageToken" ref="sentinel" class="sentinel" />
      <LoadMoreStatus
        :loading="library.favoritesLoadingMore"
        :error="library.favoritesLoadMoreError"
        @retry="loadMore"
      />
    </template>

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
