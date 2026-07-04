<script setup>
import { onMounted, ref } from 'vue'
import { ArrowLeft, History as HistoryIcon, Trash2 } from '@lucide/vue'
import { useHistoryStore } from '../stores/history'
import VideoCard from '../components/VideoCard.vue'
import AddToPlaylistModal from '../components/AddToPlaylistModal.vue'
import EmptyState from '../components/EmptyState.vue'

defineOptions({ name: 'History' })

const historyStore = useHistoryStore()
const modalVideo = ref(null)

onMounted(() => historyStore.load())

function clearHistory() {
  if (window.confirm("Vider tout l'historique ? Cette action est irréversible.")) {
    historyStore.clear()
  }
}
</script>

<template>
  <div class="page">
    <RouterLink to="/" class="back"><ArrowLeft :size="16" /> Retour</RouterLink>
    <div class="header">
      <h1>Historique</h1>
      <button
        v-if="historyStore.entries.length"
        class="link-button"
        @click="clearHistory"
      >
        <Trash2 :size="16" /> Vider l'historique
      </button>
    </div>

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
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}
h1 {
  margin: 0;
}
.link-button {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  background: transparent;
  border: none;
  color: inherit;
  opacity: 0.8;
  font-size: 0.85rem;
  cursor: pointer;
}
.link-button:hover {
  opacity: 1;
}
.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}
</style>
