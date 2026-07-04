<script setup>
import { ref, computed, onMounted, onActivated, watch } from 'vue'
import { ArrowLeft } from '@lucide/vue'
import { api } from '../api/client'
import { useLibraryStore } from '../stores/library'
import { useProgressStore } from '../stores/progress'
import { useToastStore } from '../stores/toast'
import { parseDurationSeconds } from '../utils/format'
import VideoCard from '../components/VideoCard.vue'
import AddToPlaylistModal from '../components/AddToPlaylistModal.vue'
import SkeletonCard from '../components/SkeletonCard.vue'
import EmptyState from '../components/EmptyState.vue'

defineOptions({ name: 'PlaylistDetail' })
const SKELETON_COUNT = 6

const props = defineProps({ id: { type: String, required: true } })

const library = useLibraryStore()
const progressStore = useProgressStore()
const toast = useToastStore()
const items = ref([])
const loading = ref(false)
const error = ref(null)
const modalVideo = ref(null)

const SORT_OPTIONS = [
  { value: 'position', label: 'Ordre de la playlist' },
  { value: 'title', label: 'Titre (A→Z)' },
  { value: 'newest', label: 'Plus récentes' },
  { value: 'oldest', label: 'Plus anciennes' },
  { value: 'duration', label: 'Durée (plus longues d’abord)' },
]
const filterText = ref('')
const sortKey = ref('position')

const filteredItems = computed(() => {
  const q = filterText.value.trim().toLowerCase()
  const list = q
    ? items.value.filter(
        (v) => v.title.toLowerCase().includes(q) || (v.channel || '').toLowerCase().includes(q),
      )
    : items.value.slice()

  switch (sortKey.value) {
    case 'title':
      return list.sort((a, b) => a.title.localeCompare(b.title))
    case 'newest':
      return list.sort((a, b) => new Date(b.published_at) - new Date(a.published_at))
    case 'oldest':
      return list.sort((a, b) => new Date(a.published_at) - new Date(b.published_at))
    case 'duration':
      return list.sort((a, b) => parseDurationSeconds(b.duration) - parseDurationSeconds(a.duration))
    default:
      return list.sort((a, b) => a.position - b.position)
  }
})

async function load({ silent = false } = {}) {
  if (!silent) {
    loading.value = true
    error.value = null
  }
  try {
    items.value = await api.getPlaylistItems(props.id)
    progressStore.fetchFor(items.value.map((v) => v.video_id))
  } catch (e) {
    if (!silent) error.value = e.message
  } finally {
    if (!silent) loading.value = false
  }
}

async function removeItem(video) {
  const prev = items.value
  items.value = items.value.filter((v) => v.item_id !== video.item_id)
  try {
    await api.removePlaylistItem(props.id, video.item_id)
    toast.push('Vidéo retirée de la playlist', 'success')
  } catch (e) {
    items.value = prev
    toast.push(`Échec du retrait : ${e.message}`)
  }
}

onMounted(() => {
  load()
  if (!library.playlists.length) library.loadAll()
})
// Cette vue reste en mémoire (<KeepAlive>, pour le scroll/l'état) : sans ce
// hook, revenir sur une playlist déjà visitée ne réaffiche jamais un ajout
// fait entre-temps depuis une autre page — on refetch en silence à chaque
// réactivation, sans afficher l'état "Chargement…" pour ne pas perdre le
// bénéfice du KeepAlive (contenu instantané).
onActivated(() => load({ silent: true }))
watch(() => props.id, () => load())
</script>

<template>
  <div class="playlist">
    <RouterLink to="/" class="back"><ArrowLeft :size="16" /> Retour</RouterLink>
    <div v-if="loading" class="grid">
      <SkeletonCard v-for="n in SKELETON_COUNT" :key="n" />
    </div>
    <p v-else-if="error" class="state state--error">{{ error }}</p>
    <template v-else>
      <div v-if="items.length" class="toolbar">
        <input v-model="filterText" type="search" placeholder="Filtrer par titre ou chaîne…" class="toolbar__input" />
        <select v-model="sortKey" class="toolbar__select">
          <option v-for="opt in SORT_OPTIONS" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
        </select>
      </div>

      <EmptyState v-if="!items.length" message="Cette playlist est vide." />
      <p v-else-if="!filteredItems.length" class="state">Aucune vidéo ne correspond au filtre.</p>

      <TransitionGroup v-else tag="div" name="grid" class="grid">
        <VideoCard
          v-for="v in filteredItems"
          :key="v.item_id"
          :video="v"
          removable
          @add-to-playlist="modalVideo = v"
          @remove="removeItem(v)"
        />
      </TransitionGroup>
    </template>

    <AddToPlaylistModal v-if="modalVideo" :video="modalVideo" @close="modalVideo = null" />
  </div>
</template>

<style scoped>
.playlist {
  padding: 1rem;
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
.toolbar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.toolbar__input {
  flex: 1;
  min-width: 0;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-sm);
  padding: 0.5rem 0.75rem;
  color: inherit;
  font-size: 0.9rem;
}
.toolbar__select {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-sm);
  padding: 0.5rem 0.6rem;
  color: inherit;
  font-size: 0.85rem;
}
.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  position: relative;
}
.grid-enter-active,
.grid-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}
.grid-enter-from,
.grid-leave-to {
  opacity: 0;
  transform: scale(0.9);
}
.grid-leave-active {
  position: absolute;
}
.grid-move {
  transition: transform 0.25s ease;
}
.state {
  opacity: 0.7;
}
.state--error {
  color: var(--danger);
}
</style>
