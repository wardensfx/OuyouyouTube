<template>
  <div class="skeleton-card">
    <div class="skeleton skeleton-card__thumb" />
    <div class="skeleton skeleton-card__title" />
    <div class="skeleton skeleton-card__meta" />
  </div>
</template>

<style scoped>
.skeleton-card {
  display: flex;
  flex-direction: column;
}
.skeleton-card__thumb {
  width: 100%;
  aspect-ratio: 16 / 9;
  border-radius: var(--radius-md);
}
.skeleton-card__title {
  height: 0.85rem;
  width: 90%;
  margin-top: 0.4rem;
}
.skeleton-card__meta {
  height: 0.7rem;
  width: 50%;
  margin-top: 0.35rem;
}
</style>
