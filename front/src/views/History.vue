<script setup>
import { onMounted, ref } from 'vue'
import { ArrowLeft, History as HistoryIcon } from '@lucide/vue'
import { useHistoryStore } from '../stores/history'
import VideoCard from '../components/VideoCard.vue'
import AddToPlaylistModal from '../components/AddToPlaylistModal.vue'
import EmptyState from '../components/EmptyState.vue'

defineOptions({ name: 'History' })

const historyStore = useHistoryStore()
const modalVideo = ref(null)

onMounted(() => historyStore.load())
</script>

<template>
  <div class="page">
    <RouterLink to="/" class="back"><ArrowLeft :size="16" /> Retour</RouterLink>
    <h1>Historique</h1>

    <EmptyState
      v-if="!historyStore.entries.length"
      :icon="HistoryIcon"
      message="Aucune vidéo visionnée pour l'instant."
    />

    <div v-else class="grid">
      <VideoCard
        v-for="v in historyStore.entries"
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
.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}
</style>
