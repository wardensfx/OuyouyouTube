<script setup>
import { computed, ref } from 'vue'
import { formatDuration, formatRelativeDate } from '../utils/format'

const props = defineProps({
  video: { type: Object, required: true },
  liked: { type: Boolean, default: false },
  removable: { type: Boolean, default: false },
})
const emit = defineEmits(['like', 'unlike', 'add-to-playlist', 'remove'])

const publishedLabel = computed(() => formatRelativeDate(props.video.published_at))
const durationLabel = computed(() => formatDuration(props.video.duration))

// Anti-double-clic : les actions sont async côté parent, on ne sait pas
// quand elles finissent — on bloque juste brièvement le bouton concerné.
const pending = ref(null)
function act(name) {
  if (pending.value) return
  pending.value = name
  emit(name, props.video)
  setTimeout(() => {
    pending.value = null
  }, 600)
}
</script>

<template>
  <div class="card">
    <RouterLink :to="{ name: 'player', params: { videoId: video.video_id } }" class="card__link">
      <div class="card__thumb-wrap">
        <img :src="video.thumbnail" :alt="video.title" class="card__thumb" loading="lazy" />
        <span v-if="durationLabel" class="card__duration">{{ durationLabel }}</span>
      </div>
      <p class="card__title">{{ video.title }}</p>
      <p v-if="video.channel || publishedLabel" class="card__meta">
        <span v-if="video.channel">{{ video.channel }}</span>
        <span v-if="video.channel && publishedLabel"> · </span>
        <span v-if="publishedLabel">{{ publishedLabel }}</span>
      </p>
    </RouterLink>

    <div class="card__actions">
      <button
        class="card__action"
        :class="{ 'card__action--active': liked }"
        :disabled="!!pending"
        :title="liked ? 'Retirer des favoris' : 'Ajouter aux favoris'"
        @click="act(liked ? 'unlike' : 'like')"
      >{{ liked ? '♥' : '♡' }}</button>

      <button class="card__action" :disabled="!!pending" title="Ajouter à une playlist" @click="act('add-to-playlist')">
        +
      </button>

      <button
        v-if="removable"
        class="card__action"
        :disabled="!!pending"
        title="Retirer de cette playlist"
        @click="act('remove')"
      >
        ✕
      </button>
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
.card__title {
  font-size: 0.85rem;
  margin-top: 0.4rem;
  line-height: 1.25;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.card__meta {
  font-size: 0.75rem;
  opacity: 0.6;
  margin-top: 0.15rem;
}
.card__actions {
  display: flex;
  gap: 0.4rem;
  margin-top: 0.4rem;
}
.card__action {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  color: inherit;
  cursor: pointer;
  font-size: 0.85rem;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}
.card__action:hover {
  background: var(--glass-bg-strong);
}
.card__action--active {
  color: var(--danger);
  border-color: var(--danger);
}
.card__action:disabled {
  opacity: 0.5;
  cursor: default;
}
</style>
