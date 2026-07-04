<script setup>
import { ref, onMounted, watch } from 'vue'
import { ArrowLeft } from '@lucide/vue'
import { api } from '../api/client'
import { useLibraryStore } from '../stores/library'
import { useToastStore } from '../stores/toast'
import VideoCard from '../components/VideoCard.vue'
import AddToPlaylistModal from '../components/AddToPlaylistModal.vue'

defineOptions({ name: 'PlaylistDetail' })

const props = defineProps({ id: { type: String, required: true } })

const library = useLibraryStore()
const toast = useToastStore()
const items = ref([])
const loading = ref(false)
const error = ref(null)
const modalVideo = ref(null)

async function load() {
  loading.value = true
  error.value = null
  try {
    items.value = await api.getPlaylistItems(props.id)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function removeItem(video) {
  const prev = items.value
  items.value = items.value.filter((v) => v.item_id !== video.item_id)
  try {
    await api.removePlaylistItem(props.id, video.item_id)
  } catch (e) {
    items.value = prev
    toast.push(`Échec du retrait : ${e.message}`)
  }
}

onMounted(() => {
  load()
  if (!library.playlists.length) library.loadAll()
})
watch(() => props.id, load)
</script>

<template>
  <div class="playlist">
    <RouterLink to="/" class="back"><ArrowLeft :size="16" /> Retour</RouterLink>
    <p v-if="loading" class="state">Chargement…</p>
    <p v-else-if="error" class="state state--error">{{ error }}</p>
    <TransitionGroup v-else tag="div" name="grid" class="grid">
      <VideoCard
        v-for="v in items"
        :key="v.item_id"
        :video="v"
        removable
        @add-to-playlist="modalVideo = v"
        @remove="removeItem(v)"
      />
    </TransitionGroup>

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
