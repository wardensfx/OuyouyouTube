<script setup>
import { useToastStore } from '../stores/toast'

const toast = useToastStore()
</script>

<template>
  <div class="toasts">
    <TransitionGroup name="toast">
      <div
        v-for="t in toast.items"
        :key="t.id"
        class="toast glass glass--strong"
        :class="`toast--${t.type}`"
        @click="toast.dismiss(t.id)"
      >
        {{ t.message }}
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toasts {
  position: fixed;
  left: 50%;
  bottom: calc(1.5rem + env(safe-area-inset-bottom));
  transform: translateX(-50%);
  z-index: 50;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: center;
  width: min(90vw, 420px);
}

@media (max-width: 768px) {
  .toasts {
    bottom: calc(4.5rem + env(safe-area-inset-bottom));
  }
}

.toast {
  padding: 0.65rem 1rem;
  border-radius: var(--radius-md);
  font-size: 0.85rem;
  cursor: pointer;
  width: 100%;
  text-align: center;
}
.toast--error {
  border-color: var(--danger);
}
.toast--success {
  border-color: var(--accent);
}

.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
.toast-move {
  transition: transform 0.2s ease;
}
</style>
