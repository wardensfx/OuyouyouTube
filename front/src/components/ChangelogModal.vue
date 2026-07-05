<script setup>
import { onMounted, ref } from 'vue'
import { X } from '@lucide/vue'
import { useEscapeToClose } from '../composables/useEscapeToClose'

const props = defineProps({
  version: { type: String, required: true },
})
const emit = defineEmits(['close'])

const REPO = 'wardensfx/OuyouyouTube'
const githubUrl = `https://github.com/${REPO}/blob/main/CHANGELOG.md`

const visible = ref(true)
const modalRef = ref(null)
const loading = ref(true)
const error = ref(false)
const html = ref('')

let previouslyFocused = null
onMounted(async () => {
  previouslyFocused = document.activeElement
  modalRef.value?.focus()
  await load()
})

function close() {
  visible.value = false
  previouslyFocused?.focus?.()
}
useEscapeToClose(visible, close)

async function load() {
  loading.value = true
  error.value = false
  try {
    // CHANGELOG.md vit à la racine du dépôt, hors du contexte de build
    // Docker du front (qui ne voit que front/, cf. Dockerfile) — plus simple
    // et plus fiable de le récupérer à l'exécution, à la version exacte
    // réellement déployée (tag Git posé par release-please), plutôt que de
    // le faire suivre jusque dans l'image.
    const res = await fetch(`https://raw.githubusercontent.com/${REPO}/v${props.version}/CHANGELOG.md`)
    if (!res.ok) throw new Error(`${res.status}`)
    const markdown = await res.text()
    // Chargé à la demande seulement (pas dans le bundle principal) : ce
    // n'est utile qu'à l'ouverture de cette modale, rarement consultée.
    const { marked } = await import('marked')
    html.value = marked.parse(markdown)
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <Teleport to="body">
    <Transition name="modal" @after-leave="emit('close')">
      <div v-if="visible" class="modal__backdrop" @click="close">
        <div
          ref="modalRef"
          class="modal glass glass--strong"
          role="dialog"
          aria-modal="true"
          aria-labelledby="changelog-title"
          tabindex="-1"
          @click.stop
        >
          <div class="modal__header">
            <h2 id="changelog-title" class="modal__title">Notes de version</h2>
            <button class="modal__close" title="Fermer" @click="close"><X :size="18" /></button>
          </div>

          <p v-if="loading" class="modal__state">Chargement…</p>
          <div v-else-if="error" class="modal__state">
            <p>Impossible de charger les notes de version.</p>
            <a :href="githubUrl" target="_blank" rel="noopener noreferrer" class="modal__link">Voir sur GitHub</a>
          </div>
          <!-- eslint-disable-next-line vue/no-v-html -->
          <div v-else class="modal__body" v-html="html" />
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal__backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 30;
}
.modal {
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
  width: 100%;
  max-width: 480px;
  padding: 1rem;
  max-height: 75vh;
  display: flex;
  flex-direction: column;
}
.modal:focus {
  outline: none;
}
.modal__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  margin: 0 0 0.75rem;
}
.modal__title {
  font-size: 1rem;
  margin: 0;
}
.modal__close {
  background: transparent;
  border: none;
  color: inherit;
  opacity: 0.7;
  padding: 0.25rem;
  border-radius: 50%;
  cursor: pointer;
  flex-shrink: 0;
}
.modal__close:hover {
  opacity: 1;
  background: rgba(255, 255, 255, 0.1);
}
.modal__state {
  opacity: 0.8;
  font-size: 0.9rem;
  padding: 1rem 0;
}
.modal__link {
  color: var(--accent-strong);
}
.modal__body {
  overflow-y: auto;
  font-size: 0.85rem;
  color: var(--text-dim);
}
.modal__body :deep(h1),
.modal__body :deep(h2) {
  color: var(--text);
  font-size: 1rem;
  margin: 1rem 0 0.4rem;
}
.modal__body :deep(h1:first-child),
.modal__body :deep(h2:first-child) {
  margin-top: 0;
}
.modal__body :deep(h3) {
  color: var(--text);
  font-size: 0.85rem;
  margin: 0.75rem 0 0.3rem;
}
.modal__body :deep(ul) {
  margin: 0;
  padding-left: 1.1rem;
}
.modal__body :deep(li) {
  margin: 0.3rem 0;
}
.modal__body :deep(a) {
  color: var(--accent-strong);
}
.modal__body :deep(strong) {
  color: var(--text);
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
.modal-enter-active .modal,
.modal-leave-active .modal {
  transition: transform 0.2s ease;
}
.modal-enter-from .modal,
.modal-leave-to .modal {
  transform: translateY(100%);
}
</style>
