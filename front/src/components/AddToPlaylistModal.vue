<script setup>
import { ref } from 'vue'
import { useLibraryStore } from '../stores/library'

const props = defineProps({
  video: { type: Object, default: null },
})
const emit = defineEmits(['close'])

const library = useLibraryStore()
const newTitle = ref('')
const busy = ref(false)
const visible = ref(true)

function close() {
  visible.value = false
}

async function addTo(playlistId) {
  if (!props.video || busy.value) return
  busy.value = true
  try {
    await library.addToPlaylist(playlistId, props.video)
    close()
  } finally {
    busy.value = false
  }
}

async function createAndAdd() {
  if (!newTitle.value.trim() || !props.video || busy.value) return
  busy.value = true
  try {
    const created = await library.createPlaylist(newTitle.value.trim())
    await library.addToPlaylist(created.id, props.video)
    newTitle.value = ''
    close()
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <!-- Téléporté au niveau de <body> : sans ça, un ancêtre qui pose un
       transform (ex. PullToRefresh.vue) crée un nouveau containing block
       pour position: fixed, et la modale se retrouve ancrée au bas de ce
       conteneur scrollable au lieu du viewport — invisible sans scroller. -->
  <Teleport to="body">
    <Transition name="modal" @after-leave="emit('close')">
      <div v-if="visible" class="modal__backdrop" @click="close">
        <div class="modal glass glass--strong" @click.stop>
          <h2 class="modal__title">Ajouter à une playlist</h2>

          <ul class="modal__list">
            <li v-for="p in library.playlists" :key="p.id">
              <button class="modal__row" :disabled="busy" @click="addTo(p.id)">{{ p.title }}</button>
            </li>
            <li v-if="!library.playlists.length" class="modal__empty">Aucune playlist pour l'instant.</li>
          </ul>

          <form class="modal__new" @submit.prevent="createAndAdd">
            <input v-model="newTitle" type="text" placeholder="Nouvelle playlist…" class="modal__input" />
            <button type="submit" class="modal__submit" :disabled="!newTitle.trim() || busy">Créer</button>
          </form>
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
  max-width: 420px;
  padding: 1rem;
  max-height: 70vh;
  display: flex;
  flex-direction: column;
}
.modal__title {
  font-size: 1rem;
  margin: 0 0 0.75rem;
}
.modal__list {
  list-style: none;
  margin: 0;
  padding: 0;
  overflow-y: auto;
  flex: 1;
}
.modal__row {
  display: block;
  width: 100%;
  text-align: left;
  background: transparent;
  border: none;
  color: inherit;
  padding: 0.65rem 0.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
}
.modal__row:hover {
  background: rgba(255, 255, 255, 0.1);
}
.modal__empty {
  opacity: 0.6;
  font-size: 0.85rem;
  padding: 0.5rem;
}
.modal__new {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--glass-border);
}
.modal__input {
  flex: 1;
  background: rgba(0, 0, 0, 0.25);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 0.5rem;
  color: inherit;
}
.modal__submit {
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  padding: 0.5rem 0.9rem;
  font-weight: 600;
  cursor: pointer;
}
.modal__submit:disabled {
  opacity: 0.5;
  cursor: default;
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
