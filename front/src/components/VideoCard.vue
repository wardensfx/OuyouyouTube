<script setup>
import { computed } from 'vue'
import { formatRelativeDate } from '../utils/format'

const props = defineProps({
  video: { type: Object, required: true },
  liked: { type: Boolean, default: false },
  removable: { type: Boolean, default: false },
})
defineEmits(['like', 'unlike', 'add-to-playlist', 'remove'])

const publishedLabel = computed(() => formatRelativeDate(props.video.published_at))
</script>

<template>
  <div class="card">
    <RouterLink :to="{ name: 'player', params: { videoId: video.video_id } }" class="card__link">
      <img :src="video.thumbnail" :alt="video.title" class="card__thumb" loading="lazy" />
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
        :title="liked ? 'Retirer des favoris' : 'Ajouter aux favoris'"
        @click="$emit(liked ? 'unlike' : 'like', video)"
      >{{ liked ? '♥' : '♡' }}</button>

      <button class="card__action" title="Ajouter à une playlist" @click="$emit('add-to-playlist', video)">
        +
      </button>

      <button v-if="removable" class="card__action" title="Retirer de cette playlist" @click="$emit('remove', video)">
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
.card__thumb {
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.05);
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
</style>
