<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { ArrowLeft } from '@lucide/vue'
import { api } from '../api/client'
import { useProgressStore } from '../stores/progress'
import { formatRelativeDate, formatViewCount } from '../utils/format'

const props = defineProps({ videoId: { type: String, required: true } })

const progressStore = useProgressStore()

const status = ref('idle') // idle | downloading | ready | error
const errorMessage = ref(null)
const info = ref(null)
const progress = ref(0)
const videoEl = ref(null)
let pollTimer = null
let lastReportedAt = 0

async function loadInfo() {
  try {
    info.value = await api.getVideoInfo(props.videoId)
  } catch {
    info.value = null
  }
}

function reportFinal(videoId) {
  const el = videoEl.value
  if (el && el.duration) {
    progressStore.reportProgress(videoId, el.currentTime, el.duration)
  }
}

async function start() {
  status.value = 'downloading'
  errorMessage.value = null
  info.value = null
  progress.value = 0
  lastReportedAt = 0
  try {
    await Promise.all([api.prepareVideo(props.videoId), loadInfo(), progressStore.fetchFor([props.videoId])])
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

function onLoadedMetadata() {
  const el = videoEl.value
  const saved = progressStore.items[props.videoId]
  if (
    el &&
    saved?.duration &&
    !saved.watched &&
    saved.position > 5 &&
    saved.position < saved.duration * 0.95
  ) {
    el.currentTime = saved.position
  }
}

function onTimeUpdate() {
  const el = videoEl.value
  if (!el || !el.duration) return
  const now = Date.now()
  if (now - lastReportedAt < 5000) return
  lastReportedAt = now
  progressStore.reportProgress(props.videoId, el.currentTime, el.duration)
}

const publishedLabel = computed(() => formatRelativeDate(info.value?.published_at))
const viewsLabel = computed(() => formatViewCount(info.value?.view_count))

// Raccourcis clavier façon YouTube — ignorés si focus dans un champ de
// saisie (évite d'interférer avec une éventuelle recherche/formulaire) ou
// si une touche modificatrice est pressée (laisse les raccourcis navigateur
// natifs, ex. Ctrl+F).
const SEEK_STEP = 10
const VOLUME_STEP = 0.1

function onKeydown(e) {
  const el = videoEl.value
  if (!el || status.value !== 'ready') return
  if (e.ctrlKey || e.metaKey || e.altKey) return
  const tag = e.target?.tagName
  if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || e.target?.isContentEditable) return

  switch (e.key) {
    case ' ':
    case 'k':
      e.preventDefault()
      el.paused ? el.play() : el.pause()
      break
    case 'ArrowLeft':
    case 'j':
      e.preventDefault()
      el.currentTime = Math.max(0, el.currentTime - SEEK_STEP)
      break
    case 'ArrowRight':
    case 'l':
      e.preventDefault()
      el.currentTime = Math.min(el.duration || Infinity, el.currentTime + SEEK_STEP)
      break
    case 'ArrowUp':
      e.preventDefault()
      el.volume = Math.min(1, el.volume + VOLUME_STEP)
      break
    case 'ArrowDown':
      e.preventDefault()
      el.volume = Math.max(0, el.volume - VOLUME_STEP)
      break
    case 'm':
      el.muted = !el.muted
      break
    case 'f':
      if (document.fullscreenElement) document.exitFullscreen()
      else el.requestFullscreen()
      break
  }
}

onMounted(start)
onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
  clearTimeout(pollTimer)
  reportFinal(props.videoId)
})
watch(() => props.videoId, (_newId, oldId) => {
  clearTimeout(pollTimer)
  reportFinal(oldId)
  start()
})
</script>

<template>
  <div class="player">
    <RouterLink to="/" class="back"><ArrowLeft :size="16" /> Retour</RouterLink>

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
      <video
        ref="videoEl"
        :src="api.streamUrl(videoId)"
        controls
        autoplay
        playsinline
        class="video"
        @loadedmetadata="onLoadedMetadata"
        @timeupdate="onTimeUpdate"
        @ended="reportFinal(videoId)"
      />

      <div v-if="info" class="info glass">
        <h1 class="info__title">{{ info.title }}</h1>
        <p class="info__meta">
          <RouterLink v-if="info.channel && info.channel_id" :to="{ name: 'channel', params: { id: info.channel_id } }" class="info__channel-link">
            {{ info.channel }}
          </RouterLink>
          <span v-else-if="info.channel">{{ info.channel }}</span>
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
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
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
.info__channel-link {
  color: inherit;
  text-decoration: none;
}
.info__channel-link:hover {
  text-decoration: underline;
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
@keyframes spin {
  to { transform: rotate(360deg); }
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
</style>
