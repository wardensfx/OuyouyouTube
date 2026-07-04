<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ArrowUp } from '@lucide/vue'

const visible = ref(false)

function onScroll() {
  visible.value = window.scrollY > 500
}

function toTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', onScroll))
</script>

<template>
  <Transition name="pop">
    <button v-if="visible" class="scroll-top glass" title="Remonter en haut" @click="toTop">
      <ArrowUp :size="18" />
    </button>
  </Transition>
</template>

<style scoped>
.scroll-top {
  position: fixed;
  right: 1.25rem;
  bottom: calc(1.25rem + env(safe-area-inset-bottom));
  width: 42px;
  height: 42px;
  border-radius: 50%;
  color: inherit;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 12;
}

@media (max-width: 768px) {
  .scroll-top {
    bottom: calc(4.5rem + env(safe-area-inset-bottom));
  }
}

.pop-enter-active,
.pop-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.pop-enter-from,
.pop-leave-to {
  opacity: 0;
  transform: scale(0.8);
}
</style>
