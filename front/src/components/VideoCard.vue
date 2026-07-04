<script setup>
import { computed, ref } from 'vue'
import { Heart, Plus, X, MoreVertical, Check, Eye, EyeOff } from '@lucide/vue'
import { useLibraryStore } from '../stores/library'
import { useProgressStore } from '../stores/progress'
import { formatDuration, formatRelativeDate } from '../utils/format'

const props = defineProps({
  video: { type: Object, required: true },
  removable: { type: Boolean, default: false },
  showLike: { type: Boolean, default: true },
})
const emit = defineEmits(['add-to-playlist', 'remove'])

const library = useLibraryStore()
const progressStore = useProgressStore()

const publishedLabel = computed(() => formatRelativeDate(props.video.published_at))
const durationLabel = computed(() => formatDuration(props.video.duration))
// Calculé depuis le store (pas une prop figée par le parent) : la couleur
// du cœur reste juste partout où la vidéo apparaît, y compris hors de la
// section Favoris.
const liked = computed(() => library.favorites.some((v) => v.video_id === props.video.video_id))

const progress = computed(() => progressStore.items[props.video.video_id])
const progressPercent = computed(() => {
  const p = progress.value
  if (!p || !p.duration) return 0
  return Math.min(100, Math.round((p.position / p.duration) * 100))
})
const watched = computed(() => !!progress.value?.watched)

// Anti-double-clic : les actions sont async, on bloque juste brièvement le
// bouton concerné le temps que ça se joue.
const pending = ref(null)
const pulsing = ref(false)
const menuOpen = ref(false)

async function toggleLike() {
  if (pending.value) return
  pending.value = 'like'
  pulsing.value = true
  setTimeout(() => (pulsing.value = false), 300)
  try {
    if (liked.value) await library.unlikeVideo(props.video.video_id)
    else await library.likeVideo(props.video)
  } finally {
    pending.value = null
  }
}

function act(name) {
  if (pending.value) return
  pending.value = name
  emit(name, props.video)
  setTimeout(() => {
    pending.value = null
  }, 600)
}

async function toggleWatched() {
  menuOpen.value = false
  await progressStore.setWatched(props.video.video_id, !watched.value)
}
</script>

<template>
  <div class="card">
    <RouterLink :to="{ name: 'player', params: { videoId: video.video_id } }" class="card__link">
      <div class="card__thumb-wrap">
        <img :src="video.thumbnail" :alt="video.title" class="card__thumb" loading="lazy" />
        <span v-if="durationLabel" class="card__duration">{{ durationLabel }}</span>
        <span v-if="watched" class="card__watched" title="Vue"><Check :size="12" /></span>
        <div v-if="progressPercent > 0 && !watched" class="card__progress-track">
          <div class="card__progress-fill" :style="{ width: `${progressPercent}%` }" />
        </div>
      </div>
      <p class="card__title">{{ video.title }}</p>
    </RouterLink>
    <p v-if="video.channel || publishedLabel" class="card__meta">
      <RouterLink
        v-if="video.channel && video.channel_id"
        :to="{ name: 'channel', params: { id: video.channel_id } }"
        class="card__channel-link"
      >
        {{ video.channel }}
      </RouterLink>
      <span v-else-if="video.channel">{{ video.channel }}</span>
      <span v-if="video.channel && publishedLabel"> · </span>
      <span v-if="publishedLabel">{{ publishedLabel }}</span>
    </p>

    <div class="card__actions">
      <button
        v-if="showLike"
        class="card__action"
        :class="{ 'card__action--active': liked, 'card__action--pulse': pulsing }"
        :disabled="!!pending"
        :title="liked ? 'Retirer des favoris' : 'Ajouter aux favoris'"
        @click="toggleLike"
      >
        <Heart :size="14" :fill="liked ? 'currentColor' : 'none'" />
      </button>

      <button class="card__action" :disabled="!!pending" title="Ajouter à une playlist" @click="act('add-to-playlist')">
        <Plus :size="14" />
      </button>

      <button
        v-if="removable"
        class="card__action"
        :disabled="!!pending"
        title="Retirer de cette playlist"
        @click="act('remove')"
      >
        <X :size="14" />
      </button>

      <div class="card__menu">
        <button class="card__action" title="Plus d'options" @click="menuOpen = !menuOpen">
          <MoreVertical :size="14" />
        </button>
        <div v-if="menuOpen" class="card__menu-backdrop" @click="menuOpen = false" />
        <div v-if="menuOpen" class="card__menu-panel glass glass--strong">
          <button class="card__menu-item" @click="toggleWatched">
            <component :is="watched ? EyeOff : Eye" :size="14" />
            {{ watched ? 'Marquer comme non vue' : 'Marquer comme vue' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card {
  display: flex;
  flex-direction: column;
}
.card__link {
  display: block;
  color: inherit;
  text-decoration: none;
}
.card__thumb-wrap {
  position: relative;
}
.card__thumb {
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.05);
  display: block;
}
.card__duration {
  position: absolute;
  right: 0.4rem;
  bottom: 0.4rem;
  background: rgba(0, 0, 0, 0.75);
  color: #fff;
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.05rem 0.35rem;
  border-radius: 4px;
}
.card__watched {
  position: absolute;
  left: 0.4rem;
  top: 0.4rem;
  background: var(--accent);
  color: #fff;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.card__progress-track {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 3px;
  background: rgba(255, 255, 255, 0.25);
  border-radius: 0 0 var(--radius-md) var(--radius-md);
  overflow: hidden;
}
.card__progress-fill {
  height: 100%;
  background: var(--danger);
}
.card__title {
  font-size: 0.85rem;
  margin: 0.25rem 0 0;
  line-height: 1.25;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.card__meta {
  font-size: 0.75rem;
  opacity: 0.6;
  margin: 0.1rem 0 0;
}
.card__channel-link {
  color: inherit;
  text-decoration: none;
}
.card__channel-link:hover {
  text-decoration: underline;
}
.card__actions {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  margin-top: 0.25rem;
}
.card__action {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  color: inherit;
  cursor: pointer;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.15s ease, border-color 0.15s ease;
}
.card__action:hover {
  background: var(--glass-bg-strong);
}
.card__action--active {
  color: var(--danger);
  border-color: var(--danger);
}
.card__action--pulse {
  animation: heart-pulse 0.3s ease;
}
@keyframes heart-pulse {
  0% {
    transform: scale(1);
  }
  40% {
    transform: scale(1.35);
  }
  100% {
    transform: scale(1);
  }
}
.card__action:disabled {
  opacity: 0.5;
  cursor: default;
}
.card__menu {
  position: relative;
  margin-left: auto;
}
.card__menu-backdrop {
  position: fixed;
  inset: 0;
  z-index: 20;
}
.card__menu-panel {
  position: absolute;
  right: 0;
  top: calc(100% + 0.3rem);
  border-radius: var(--radius-md);
  padding: 0.3rem;
  min-width: 180px;
  z-index: 21;
}
.card__menu-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  background: transparent;
  border: none;
  color: inherit;
  text-align: left;
  padding: 0.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.8rem;
}
.card__menu-item:hover {
  background: rgba(255, 255, 255, 0.1);
}
</style>
