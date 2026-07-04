<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { api } from '../api/client'
import { formatRelativeDate, formatViewCount } from '../utils/format'

const props = defineProps({ videoId: { type: String, required: true } })

const status = ref('idle') // idle | downloading | ready | error
const errorMessage = ref(null)
const info = ref(null)
const progress = ref(0)
let pollTimer = null

async function loadInfo() {
  try {
    info.value = await api.getVideoInfo(props.videoId)
  } catch {
    info.value = null
  }
}

async function start() {
  status.value = 'downloading'
  errorMessage.value = null
  info.value = null
  progress.value = 0
  try {
    await Promise.all([api.prepareVideo(props.videoId), loadInfo()])
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
    if (s.progress !== undefined) progress.value = Number(s.progress)
    pollTimer = setTimeout(poll, 1500)
  } catch (e) {
    status.value = 'error'
    errorMessage.value = e.message
  }
}

const publishedLabel = computed(() => formatRelativeDate(info.value?.published_at))
const viewsLabel = computed(() => formatViewCount(info.value?.view_count))

onMounted(start)
onUnmounted(() => clearTimeout(pollTimer))
watch(() => props.videoId, () => {
  clearTimeout(pollTimer)
  start()
})
</script>

<template>
  <div class="player">
    <RouterLink to="/" class="back">← Retour</RouterLink>

    <div v-if="status === 'downloading'" class="state">
      <div class="spinner" />
      <p>{{ info?.title ? `Préparation de « ${info.title} »…` : 'Préparation de la vidéo…' }}</p>
      <div class="progress">
        <div class="progress__bar" :style="{ width: `${progress}%` }" />
      </div>
      <p class="progress__label">{{ progress }} %</p>
    </div>

    <p v-else-if="status === 'error'" class="state state--error">
      {{ errorMessage }}
    </p>

    <template v-else-if="status === 'ready'">
      <video :src="api.streamUrl(videoId)" controls autoplay playsinline class="video" />

      <div v-if="info" class="info glass">
        <h1 class="info__title">{{ info.title }}</h1>
        <p class="info__meta">
          <span v-if="info.channel">{{ info.channel }}</span>
          <span v-if="info.channel && (viewsLabel || publishedLabel)"> · </span>
          <span v-if="viewsLabel">{{ viewsLabel }}</span>
          <span v-if="viewsLabel && publishedLabel"> · </span>
          <span v-if="publishedLabel">{{ publishedLabel }}</span>
        </p>
        <p v-if="info.description" class="info__description">{{ info.description }}</p>
      </div>
    </template>
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
  border-radius: var(--radius-lg);
  background: #000;
}
.info {
  margin-top: 1rem;
  padding: 1rem;
  border-radius: var(--radius-lg);
}
.info__title {
  font-size: 1.1rem;
  margin: 0 0 0.4rem;
}
.info__meta {
  font-size: 0.85rem;
  color: var(--text-dim);
  margin: 0;
}
.info__description {
  font-size: 0.85rem;
  color: var(--text-dim);
  margin-top: 0.75rem;
  white-space: pre-wrap;
  max-height: 8rem;
  overflow-y: auto;
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
  color: var(--danger);
}
.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #333;
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
.progress {
  width: 100%;
  max-width: 320px;
  height: 6px;
  border-radius: var(--radius-pill);
  background: rgba(255, 255, 255, 0.1);
  overflow: hidden;
}
.progress__bar {
  height: 100%;
  background: var(--accent);
  transition: width 0.3s ease;
}
.progress__label {
  font-size: 0.8rem;
  color: var(--text-dim);
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
