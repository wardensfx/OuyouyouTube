<script setup>
import { onMounted, ref } from 'vue'
import { ArrowLeft, Pencil, Trash2, Check, X, ChevronUp, ChevronDown, Plus, ListMusic } from '@lucide/vue'
import { useLibraryStore } from '../stores/library'
import { usePlaylistOrder } from '../composables/usePlaylistOrder'
import EmptyState from '../components/EmptyState.vue'

defineOptions({ name: 'ManagePlaylists' })
const SKELETON_COUNT = 4

const library = useLibraryStore()
onMounted(() => {
  if (!library.playlists.length) library.loadAll()
})

const { ordered, move } = usePlaylistOrder(() => library.playlists)

const editingId = ref(null)
const editingTitle = ref('')
const confirmingId = ref(null)
const newTitle = ref('')

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

async function createPlaylist() {
  const title = newTitle.value.trim()
  if (!title) return
  newTitle.value = ''
  await library.createPlaylist(title)
}
</script>

<template>
  <div class="manage">
    <RouterLink to="/" class="back"><ArrowLeft :size="16" /> Retour</RouterLink>
    <h1>Gérer les playlists</h1>

    <form class="new-playlist" @submit.prevent="createPlaylist">
      <input v-model="newTitle" type="text" placeholder="Nouvelle playlist…" class="new-playlist__input" />
      <button type="submit" class="new-playlist__submit" :disabled="!newTitle.trim()">
        <Plus :size="16" /> Créer
      </button>
    </form>

    <ul v-if="library.loading" class="list">
      <li v-for="n in SKELETON_COUNT" :key="n" class="row glass">
        <div class="skeleton row__thumb-skeleton" />
        <div class="row__body">
          <div class="skeleton row__title-skeleton" />
          <div class="skeleton row__meta-skeleton" />
        </div>
      </li>
    </ul>
    <EmptyState v-else-if="!ordered.length" :icon="ListMusic" message="Aucune playlist pour l'instant." />

    <TransitionGroup v-else tag="ul" name="row" class="list">
      <li v-for="(p, index) in ordered" :key="p.id" class="row glass">
        <div class="row__order">
          <button class="row__icon-btn" :disabled="index === 0" title="Monter" @click="move(p.id, -1)">
            <ChevronUp :size="14" />
          </button>
          <button class="row__icon-btn" :disabled="index === ordered.length - 1" title="Descendre" @click="move(p.id, 1)">
            <ChevronDown :size="14" />
          </button>
        </div>

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
    </TransitionGroup>
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
.new-playlist {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.new-playlist__input {
  flex: 1;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-sm);
  padding: 0.6rem 0.75rem;
  color: inherit;
}
.new-playlist__submit {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  padding: 0.6rem 1rem;
  font-weight: 600;
  cursor: pointer;
}
.new-playlist__submit:disabled {
  opacity: 0.5;
  cursor: default;
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
  position: relative;
}
.row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.5rem;
  border-radius: var(--radius-md);
  position: relative;
}
.row-move {
  transition: transform 0.2s ease;
}
.row-enter-active,
.row-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.row-enter-from,
.row-leave-to {
  opacity: 0;
  transform: scale(0.95);
}
.row-leave-active {
  position: absolute;
  width: 100%;
}
.row__order {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  flex-shrink: 0;
}
.row__order .row__icon-btn {
  width: 22px;
  height: 22px;
}
/* Empilés verticalement avec un gap de 0.15rem (2.4px) : l'agrandissement
   de la zone tactile (cf. #93) va surtout à l'horizontale, où il n'y a pas
   de voisin à côté, plutôt qu'à la verticale où les deux boutons se
   toucheraient. */
.row__order .row__icon-btn::before {
  inset: -1px -11px;
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
.row__thumb-skeleton {
  width: 96px;
  aspect-ratio: 16 / 9;
  border-radius: var(--radius-sm);
  flex-shrink: 0;
}
.row__title-skeleton {
  height: 0.9rem;
  width: 60%;
  border-radius: 4px;
}
.row__meta-skeleton {
  height: 0.75rem;
  width: 35%;
  margin-top: 0.4rem;
  border-radius: 4px;
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
  position: relative;
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
/* Élargit la zone tactile sans agrandir le rendu visuel (cf. #93) : ces
   boutons sont serrés les uns contre les autres à l'horizontale (gap
   0.3rem = 4.8px), donc l'agrandissement horizontal reste modéré — la
   marge la plus généreuse va verticalement. `.row__order .row__icon-btn`
   (empilage vertical) inverse ce compromis, voir plus haut. */
.row__icon-btn::before {
  content: '';
  position: absolute;
  inset: -7px -2px;
}
.row__icon-btn:hover {
  background: rgba(255, 255, 255, 0.12);
}
.row__icon-btn:disabled {
  opacity: 0.3;
  cursor: default;
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
