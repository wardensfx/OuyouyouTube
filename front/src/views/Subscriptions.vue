<script setup>
import { computed, onMounted, ref } from 'vue'
import { ArrowLeft } from '@lucide/vue'
import { api } from '../api/client'
import { useProgressStore } from '../stores/progress'
import VideoCard from '../components/VideoCard.vue'
import AddToPlaylistModal from '../components/AddToPlaylistModal.vue'
import SkeletonCard from '../components/SkeletonCard.vue'
import EmptyState from '../components/EmptyState.vue'

defineOptions({ name: 'Subscriptions' })
const SKELETON_COUNT = 6

const progressStore = useProgressStore()
const videos = ref([])
// Vidéo déjà vue = hors du flux de découverte (contrairement aux
// Favoris/Playlists, qu'on constitue soi-même).
const visibleVideos = computed(() => videos.value.filter((v) => !progressStore.items[v.video_id]?.watched))
const loading = ref(false)
const error = ref(null)
const modalVideo = ref(null)

async function load() {
  loading.value = true
  error.value = null
  try {
    videos.value = await api.getSubscriptionsFeed()
    progressStore.fetchFor(videos.value.map((v) => v.video_id))
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="page">
    <RouterLink to="/" class="back"><ArrowLeft :size="16" /> Retour</RouterLink>
    <h1>Abonnements</h1>

    <div v-if="loading" class="grid">
      <SkeletonCard v-for="n in SKELETON_COUNT" :key="n" />
    </div>
    <p v-else-if="error" class="state state--error">{{ error }}</p>
    <EmptyState v-else-if="!visibleVideos.length" message="Rien de nouveau pour l'instant." />

    <div v-else class="grid">
      <VideoCard
        v-for="v in visibleVideos"
        :key="v.video_id"
        :video="v"
        @add-to-playlist="modalVideo = v"
      />
    </div>

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
}
.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}
</style>
