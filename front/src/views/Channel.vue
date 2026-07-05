<script setup>
import { onMounted, ref, watch } from 'vue'
import { ArrowLeft } from '@lucide/vue'
import { api } from '../api/client'
import { useProgressStore } from '../stores/progress'
import { formatSubscriberCount } from '../utils/format'
import { useInfiniteScroll } from '../composables/useInfiniteScroll'
import VideoCard from '../components/VideoCard.vue'
import AddToPlaylistModal from '../components/AddToPlaylistModal.vue'
import LoadMoreStatus from '../components/LoadMoreStatus.vue'
import SkeletonCard from '../components/SkeletonCard.vue'
import EmptyState from '../components/EmptyState.vue'

defineOptions({ name: 'Channel' })
const SKELETON_COUNT = 6

const props = defineProps({ id: { type: String, required: true } })

const progressStore = useProgressStore()
const channel = ref(null)
const videos = ref([])
const loading = ref(false)
const loadingMore = ref(false)
const error = ref(null)
// Séparée de `error` (chargement initial) : un échec de page suivante ne
// doit pas remplacer toute la page déjà affichée par un état d'erreur.
const loadMoreError = ref(null)
const nextPageToken = ref(null)
const modalVideo = ref(null)

async function load() {
  loading.value = true
  error.value = null
  channel.value = null
  videos.value = []
  nextPageToken.value = null
  try {
    const [info, channelVideos] = await Promise.all([api.getChannel(props.id), api.getChannelVideos(props.id)])
    channel.value = info
    videos.value = channelVideos.items
    nextPageToken.value = channelVideos.next_page_token
    progressStore.fetchFor(videos.value.map((v) => v.video_id))
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function loadMore() {
  if (!nextPageToken.value || loadingMore.value) return
  loadingMore.value = true
  loadMoreError.value = null
  try {
    const page = await api.getChannelVideos(props.id, nextPageToken.value)
    videos.value = [...videos.value, ...page.items]
    nextPageToken.value = page.next_page_token
    progressStore.fetchFor(page.items.map((v) => v.video_id))
  } catch (e) {
    loadMoreError.value = e.message
  } finally {
    loadingMore.value = false
  }
}
const { sentinel } = useInfiniteScroll(loadMore)

onMounted(load)
watch(() => props.id, load)
</script>

<template>
  <div class="page">
    <RouterLink to="/" class="back"><ArrowLeft :size="16" /> Retour</RouterLink>

    <div v-if="loading" class="grid">
      <SkeletonCard v-for="n in SKELETON_COUNT" :key="n" />
    </div>
    <div v-else-if="error" class="state state--error">
      <p>{{ error }}</p>
      <button class="retry-btn" @click="load">Réessayer</button>
    </div>

    <template v-else-if="channel">
      <div class="header glass">
        <img v-if="channel.thumbnail" :src="channel.thumbnail" :alt="channel.title" class="header__avatar" />
        <div class="header__info">
          <h1 class="header__title">{{ channel.title }}</h1>
          <p v-if="formatSubscriberCount(channel.subscriber_count)" class="header__meta">
            {{ formatSubscriberCount(channel.subscriber_count) }}
          </p>
          <p v-if="channel.description" class="header__description">{{ channel.description }}</p>
        </div>
      </div>

      <div class="grid">
        <VideoCard
          v-for="v in videos"
          :key="v.video_id"
          :video="v"
          @add-to-playlist="modalVideo = v"
        />
      </div>
      <div v-if="nextPageToken" ref="sentinel" class="sentinel" />
      <LoadMoreStatus :loading="loadingMore" :error="loadMoreError" @retry="loadMore" />
      <EmptyState v-if="!videos.length" message="Aucune vidéo pour l'instant." />
    </template>

    <AddToPlaylistModal v-if="modalVideo" :video="modalVideo" @close="modalVideo = null" />
  </div>
</template>

<style scoped>
.page {
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
.state {
  opacity: 0.7;
}
.state--error {
  color: var(--danger);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.5rem;
}
.retry-btn {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-pill);
  color: inherit;
  padding: 0.4rem 0.9rem;
  font-size: 0.85rem;
  cursor: pointer;
}
.header {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  padding: 1rem;
  border-radius: var(--radius-lg);
  margin-bottom: 1.25rem;
}
.header__avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
}
.header__info {
  min-width: 0;
}
.header__title {
  margin: 0 0 0.2rem;
  font-size: 1.1rem;
  /* Un nom de chaîne inhabituellement long et non sécable reposerait sinon
     uniquement sur le filet de sécurité global overflow-x: hidden et se
     couperait silencieusement au lieu de passer à la ligne — même raison
     que .header__description ci-dessous. */
  overflow-wrap: anywhere;
}
.header__meta {
  margin: 0;
  font-size: 0.85rem;
  color: var(--text-dim);
}
.header__description {
  margin-top: 0.5rem;
  font-size: 0.85rem;
  color: var(--text-dim);
  white-space: pre-wrap;
  /* Bio de chaîne contient souvent une URL longue et non coupée — sans ça
     elle déborde hors de sa boîte, élargit toute la page horizontalement,
     et décale visuellement la grille de vignettes en dessous (ce qui les
     fait paraître de tailles différentes alors que leur CSS est identique). */
  overflow-wrap: anywhere;
  max-height: 6rem;
  overflow-y: auto;
}
.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}
.sentinel {
  height: 1px;
}
</style>
