<script setup>
defineProps({ video: { type: Object, required: true } })
</script>

<template>
  <RouterLink :to="{ name: 'player', params: { videoId: video.video_id } }" class="card">
    <img :src="video.thumbnail" :alt="video.title" class="card__thumb" loading="lazy" />
    <p class="card__title">{{ video.title }}</p>
    <p v-if="video.channel" class="card__meta">{{ video.channel }}</p>
  </RouterLink>
</template>

<style scoped>
.card {
  display: block;
  color: inherit;
  text-decoration: none;
}
.card__thumb {
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  border-radius: 10px;
  background: #222;
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
</style>
