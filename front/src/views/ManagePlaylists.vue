<script setup>
import { onMounted, ref } from 'vue'
import { ArrowLeft, Pencil, Trash2, Check, X } from '@lucide/vue'
import { useLibraryStore } from '../stores/library'

defineOptions({ name: 'ManagePlaylists' })

const library = useLibraryStore()
onMounted(() => {
  if (!library.playlists.length) library.loadAll()
})

const editingId = ref(null)
const editingTitle = ref('')
const confirmingId = ref(null)

function startEdit(playlist) {
  editingId.value = playlist.id
  editingTitle.value = playlist.title
}

function cancelEdit() {
  editingId.value = null
}

async function saveEdit(playlist) {
  const title = editingTitle.value.trim()
  editingId.value = null
  if (!title || title === playlist.title) return
  await library.renamePlaylist(playlist.id, title)
}

async function confirmDelete(playlist) {
  if (confirmingId.value !== playlist.id) {
    confirmingId.value = playlist.id
    return
  }
  confirmingId.value = null
  await library.deletePlaylist(playlist.id)
}
</script>

<template>
  <div class="manage">
    <RouterLink to="/" class="back"><ArrowLeft :size="16" /> Retour</RouterLink>
    <h1>Gérer les playlists</h1>

    <p v-if="library.loading" class="state">Chargement…</p>
    <p v-else-if="!library.playlists.length" class="state">Aucune playlist pour l'instant.</p>

    <ul v-else class="list">
      <li v-for="p in library.playlists" :key="p.id" class="row glass">
        <img :src="p.thumbnail" class="row__thumb" :alt="p.title" />

        <div class="row__body">
          <form v-if="editingId === p.id" class="row__edit" @submit.prevent="saveEdit(p)">
            <input v-model="editingTitle" type="text" class="row__input" autofocus />
            <button type="submit" class="row__icon-btn" title="Valider"><Check :size="16" /></button>
            <button type="button" class="row__icon-btn" title="Annuler" @click="cancelEdit"><X :size="16" /></button>
          </form>
          <template v-else>
            <p class="row__title">{{ p.title }}</p>
            <p class="row__meta">{{ p.item_count }} vidéos</p>
          </template>
        </div>

        <div v-if="editingId !== p.id" class="row__actions">
          <button class="row__icon-btn" title="Renommer" @click="startEdit(p)"><Pencil :size="16" /></button>
          <button
            class="row__icon-btn"
            :class="{ 'row__icon-btn--danger': confirmingId === p.id }"
            :title="confirmingId === p.id ? 'Confirmer la suppression' : 'Supprimer'"
            @click="confirmDelete(p)"
          >
            <Trash2 :size="16" />
          </button>
        </div>
        <span v-if="confirmingId === p.id" class="row__confirm">Cliquer encore pour confirmer</span>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.manage {
  padding: 1rem;
  max-width: 640px;
  margin: 0 auto;
}
.back {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  margin-bottom: 1rem;
  color: inherit;
  opacity: 0.7;
  text-decoration: none;
}
h1 {
  margin-bottom: 1rem;
}
.state {
  opacity: 0.7;
}
.list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  border-radius: var(--radius-md);
  position: relative;
}
.row__thumb {
  width: 96px;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.05);
  flex-shrink: 0;
}
.row__body {
  flex: 1;
  min-width: 0;
}
.row__title {
  font-size: 0.9rem;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.row__meta {
  font-size: 0.75rem;
  color: var(--text-dim);
  margin: 0.15rem 0 0;
}
.row__edit {
  display: flex;
  align-items: center;
  gap: 0.3rem;
}
.row__input {
  flex: 1;
  background: rgba(0, 0, 0, 0.25);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-sm);
  padding: 0.4rem 0.5rem;
  color: inherit;
  min-width: 0;
}
.row__actions {
  display: flex;
  gap: 0.3rem;
  flex-shrink: 0;
}
.row__icon-btn {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  border: 1px solid var(--glass-border);
  background: rgba(255, 255, 255, 0.06);
  color: inherit;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.row__icon-btn:hover {
  background: rgba(255, 255, 255, 0.12);
}
.row__icon-btn--danger {
  color: var(--danger);
  border-color: var(--danger);
}
.row__confirm {
  position: absolute;
  right: 0.5rem;
  bottom: -1.1rem;
  font-size: 0.7rem;
  color: var(--danger);
}
</style>
