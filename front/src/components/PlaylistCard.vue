<script setup>
defineProps({ playlist: { type: Object, required: true } })
</script>

<template>
  <RouterLink :to="{ name: 'playlist', params: { id: playlist.id } }" class="card">
    <img :src="playlist.thumbnail" :alt="playlist.title" class="card__thumb" loading="lazy" />
    <p class="card__title">{{ playlist.title }}</p>
    <p class="card__meta">{{ playlist.item_count }} vidéos</p>
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
