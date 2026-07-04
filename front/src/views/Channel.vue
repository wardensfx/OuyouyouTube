<script setup>
import { onMounted, ref, watch } from 'vue'
import { ArrowLeft } from '@lucide/vue'
import { api } from '../api/client'
import { useProgressStore } from '../stores/progress'
import { formatSubscriberCount } from '../utils/format'
import VideoCard from '../components/VideoCard.vue'
import AddToPlaylistModal from '../components/AddToPlaylistModal.vue'

defineOptions({ name: 'Channel' })

const props = defineProps({ id: { type: String, required: true } })

const progressStore = useProgressStore()
const channel = ref(null)
const videos = ref([])
const loading = ref(false)
const error = ref(null)
const modalVideo = ref(null)

async function load() {
  loading.value = true
  error.value = null
  channel.value = null
  videos.value = []
  try {
    const [info, channelVideos] = await Promise.all([api.getChannel(props.id), api.getChannelVideos(props.id)])
    channel.value = info
    videos.value = channelVideos
    progressStore.fetchFor(videos.value.map((v) => v.video_id))
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(load)
watch(() => props.id, load)
</script>

<template>
  <div class="page">
    <RouterLink to="/" class="back"><ArrowLeft :size="16" /> Retour</RouterLink>

    <p v-if="loading" class="state">Chargement…</p>
    <p v-else-if="error" class="state state--error">{{ error }}</p>

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
      <p v-if="!videos.length" class="state">Aucune vidéo pour l'instant.</p>
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
  max-height: 6rem;
  overflow-y: auto;
}
.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}
</style>
