<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { api } from '../api/client'

const props = defineProps({ videoId: { type: String, required: true } })

const status = ref('idle') // idle | downloading | ready | error
const errorMessage = ref(null)
let pollTimer = null

async function start() {
  status.value = 'downloading'
  try {
    await api.prepareVideo(props.videoId)
    poll()
  } catch (e) {
    status.value = 'error'
    errorMessage.value = e.message
  }
}

async function poll() {
  try {
    const s = await api.getVideoStatus(props.videoId)
    if (s.state === 'ready') {
      status.value = 'ready'
      return
    }
    if (s.state === 'error') {
      status.value = 'error'
      errorMessage.value = s.error || 'Échec du téléchargement'
      return
    }
    pollTimer = setTimeout(poll, 1500)
  } catch (e) {
    status.value = 'error'
    errorMessage.value = e.message
  }
}

onMounted(start)
onUnmounted(() => clearTimeout(pollTimer))
</script>

<template>
  <div class="player">
    <RouterLink to="/" class="back">← Retour</RouterLink>

    <div v-if="status === 'downloading'" class="state">
      <div class="spinner" />
      <p>Préparation de la vidéo…</p>
    </div>

    <p v-else-if="status === 'error'" class="state state--error">
      {{ errorMessage }}
    </p>

    <video
      v-else-if="status === 'ready'"
      :src="api.streamUrl(videoId)"
      controls
      autoplay
      playsinline
      class="video"
    />
  </div>
</template>

<style scoped>
.player {
  padding: 1rem;
}
.back {
  display: inline-block;
  margin-bottom: 1rem;
  color: inherit;
  opacity: 0.7;
  text-decoration: none;
}
.video {
  width: 100%;
  border-radius: 10px;
  background: #000;
}
.state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 3rem 0;
  opacity: 0.8;
}
.state--error {
  color: #ff6b6b;
}
.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #333;
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
