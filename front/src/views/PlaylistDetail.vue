<script setup>
import { ref, onMounted, watch } from 'vue'
import { api } from '../api/client'
import VideoCard from '../components/VideoCard.vue'

const props = defineProps({ id: { type: String, required: true } })

const items = ref([])
const loading = ref(false)
const error = ref(null)

async function load() {
  loading.value = true
  error.value = null
  try {
    items.value = await api.getPlaylistItems(props.id)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(load)
watch(() => props.id, load)
</script>

<template>
  <div class="playlist">
    <RouterLink to="/" class="back">← Retour</RouterLink>
    <p v-if="loading" class="state">Chargement…</p>
    <p v-else-if="error" class="state state--error">{{ error }}</p>
    <div v-else class="grid">
      <VideoCard v-for="v in items" :key="v.video_id" :video="v" />
    </div>
  </div>
</template>

<style scoped>
.playlist {
  padding: 1rem;
}
.back {
  display: inline-block;
  margin-bottom: 1rem;
  color: inherit;
  opacity: 0.7;
  text-decoration: none;
}
.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}
.state {
  opacity: 0.7;
}
.state--error {
  color: #ff6b6b;
}
</style>
