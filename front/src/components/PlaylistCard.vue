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
  /* Sans ça, un item de grille grid-template-columns garde un min-width
     égal au min-content de son contenu : un titre avec un token non-sécable
     (URL, hashtag) peut alors gonfler sa colonne bien au-delà de 1fr et
     pousser toute la grille en overflow horizontal (même bug que VideoCard,
     cf. #77, jamais corrigé ici — #94). */
  min-width: 0;
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
</style>
