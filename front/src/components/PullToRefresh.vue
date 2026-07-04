<script setup>
import { ref } from 'vue'
import { RefreshCw } from '@lucide/vue'

const props = defineProps({
  refresh: { type: Function, required: true },
})

const THRESHOLD = 70
const MAX_PULL = 100

const pullDistance = ref(0)
const dragging = ref(false)
const refreshing = ref(false)
let startY = 0
let active = false

function onTouchStart(e) {
  // Seulement si on est déjà tout en haut de la page — sinon c'est un
  // scroll normal, pas un tiré-pour-rafraîchir.
  if (refreshing.value || window.scrollY > 0) return
  active = true
  dragging.value = true
  startY = e.touches[0].clientY
}

function onTouchMove(e) {
  if (!active) return
  const delta = e.touches[0].clientY - startY
  if (delta <= 0) {
    active = false
    dragging.value = false
    pullDistance.value = 0
    return
  }
  // Résistance : le tiré ralentit au fur et à mesure (pattern natif).
  pullDistance.value = Math.min(delta * 0.5, MAX_PULL)
}

async function onTouchEnd() {
  if (!active) return
  active = false
  dragging.value = false
  if (pullDistance.value >= THRESHOLD) {
    refreshing.value = true
    pullDistance.value = THRESHOLD
    try {
      await props.refresh()
    } finally {
      refreshing.value = false
      pullDistance.value = 0
    }
  } else {
    pullDistance.value = 0
  }
}
</script>

<template>
  <div class="ptr" @touchstart="onTouchStart" @touchmove="onTouchMove" @touchend="onTouchEnd">
    <div class="ptr__indicator" :style="{ opacity: Math.min(pullDistance / THRESHOLD, 1) }">
      <RefreshCw
        :size="20"
        class="ptr__icon"
        :class="{ 'ptr__icon--spin': refreshing }"
        :style="refreshing ? {} : { transform: `rotate(${Math.min(pullDistance / THRESHOLD, 1) * 180}deg)` }"
      />
    </div>
    <div
      class="ptr__content"
      :style="{ transform: `translateY(${pullDistance}px)`, transition: dragging ? 'none' : 'transform 0.2s ease' }"
    >
      <slot />
    </div>
  </div>
</template>

<style scoped>
.ptr {
  position: relative;
}
.ptr__indicator {
  position: absolute;
  top: 0.75rem;
  left: 50%;
  transform: translateX(-50%);
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-dim);
  pointer-events: none;
}
.ptr__icon--spin {
  animation: ptr-spin 0.8s linear infinite;
}
@keyframes ptr-spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
