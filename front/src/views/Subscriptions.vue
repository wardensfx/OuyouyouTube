<script setup>
import { onMounted, ref } from 'vue'
import { ArrowLeft } from '@lucide/vue'
import { api } from '../api/client'
import VideoCard from '../components/VideoCard.vue'
import AddToPlaylistModal from '../components/AddToPlaylistModal.vue'

defineOptions({ name: 'Subscriptions' })

const videos = ref([])
const loading = ref(false)
const error = ref(null)
const modalVideo = ref(null)

async function load() {
  loading.value = true
  error.value = null
  try {
    videos.value = await api.getSubscriptionsFeed()
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

    <p v-if="loading" class="state">Chargement…</p>
    <p v-else-if="error" class="state state--error">{{ error }}</p>
    <p v-else-if="!videos.length" class="state">Rien de nouveau pour l'instant.</p>

    <div v-else class="grid">
      <VideoCard
        v-for="v in videos"
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
