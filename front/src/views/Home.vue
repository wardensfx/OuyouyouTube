<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../api/client'
import { useLibraryStore } from '../stores/library'
import VideoCard from '../components/VideoCard.vue'
import PlaylistCard from '../components/PlaylistCard.vue'
import AddToPlaylistModal from '../components/AddToPlaylistModal.vue'

const library = useLibraryStore()
onMounted(() => library.loadAll())

const modalVideo = ref(null)
const creating = ref(false)
const newPlaylistTitle = ref('')

async function submitNewPlaylist() {
  if (!newPlaylistTitle.value.trim()) return
  await library.createPlaylist(newPlaylistTitle.value.trim())
  newPlaylistTitle.value = ''
  creating.value = false
}

const subscriptions = ref([])
const subscriptionsLoading = ref(false)
const subscriptionsError = ref(null)

const trending = ref([])
const trendingLoading = ref(false)
const trendingError = ref(null)

async function loadSubscriptions() {
  subscriptionsLoading.value = true
  subscriptionsError.value = null
  try {
    subscriptions.value = await api.getSubscriptionsFeed()
  } catch (e) {
    subscriptionsError.value = e.message
  } finally {
    subscriptionsLoading.value = false
  }
}

async function loadTrending() {
  trendingLoading.value = true
  trendingError.value = null
  try {
    trending.value = await api.getTrending()
  } catch (e) {
    trendingError.value = e.message
  } finally {
    trendingLoading.value = false
  }
}

onMounted(() => {
  loadSubscriptions()
  loadTrending()
})
</script>

<template>
  <div class="home">
    <header class="home__header">
      <h1>Accueil</h1>
    </header>

    <section class="section">
      <h2>Abonnements</h2>
      <p v-if="subscriptionsLoading" class="state">Chargement…</p>
      <p v-else-if="subscriptionsError" class="state state--error">{{ subscriptionsError }}</p>
      <p v-else-if="!subscriptions.length" class="state">Rien de nouveau pour l'instant.</p>
      <div v-else class="grid">
        <VideoCard
          v-for="v in subscriptions"
          :key="v.video_id"
          :video="v"
          @like="library.likeVideo(v.video_id)"
          @add-to-playlist="modalVideo = v"
        />
      </div>
    </section>

    <section class="section">
      <h2>Tendances</h2>
      <p v-if="trendingLoading" class="state">Chargement…</p>
      <p v-else-if="trendingError" class="state state--error">{{ trendingError }}</p>
      <div v-else class="grid">
        <VideoCard
          v-for="v in trending"
          :key="v.video_id"
          :video="v"
          @like="library.likeVideo(v.video_id)"
          @add-to-playlist="modalVideo = v"
        />
      </div>
    </section>

    <p v-if="library.loading" class="state">Chargement…</p>
    <p v-else-if="library.error" class="state state--error">{{ library.error }}</p>

    <template v-else>
      <section class="section">
        <div class="section__header">
          <h2>Playlists</h2>
          <button class="link-button" @click="creating = !creating">+ Nouvelle</button>
        </div>

        <form v-if="creating" class="new-playlist" @submit.prevent="submitNewPlaylist">
          <input v-model="newPlaylistTitle" type="text" placeholder="Titre de la playlist…" class="new-playlist__input" />
          <button type="submit" class="new-playlist__submit" :disabled="!newPlaylistTitle.trim()">Créer</button>
        </form>

        <div class="grid">
          <PlaylistCard v-for="p in library.playlists" :key="p.id" :playlist="p" />
        </div>
      </section>

      <section class="section">
        <h2>Favoris</h2>
        <div class="grid">
          <VideoCard
            v-for="v in library.favorites"
            :key="v.video_id"
            :video="v"
            liked
            @unlike="library.unlikeVideo(v.video_id)"
            @add-to-playlist="modalVideo = v"
          />
        </div>
      </section>
    </template>

    <AddToPlaylistModal v-if="modalVideo" :video="modalVideo" @close="modalVideo = null" />
  </div>
</template>

<style scoped>
.home__header {
  padding: 1rem;
}
.section {
  padding: 0 1rem 1.5rem;
}
.section__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}
.section h2 {
  font-size: 1rem;
  opacity: 0.7;
  margin: 0 0 0.75rem;
}
.link-button {
  background: transparent;
  border: none;
  color: inherit;
  opacity: 0.8;
  font-size: 0.85rem;
  cursor: pointer;
}
.link-button:hover {
  opacity: 1;
}
.new-playlist {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}
.new-playlist__input {
  flex: 1;
  background: #181818;
  border: 1px solid #2a2a2a;
  border-radius: 8px;
  padding: 0.5rem;
  color: inherit;
}
.new-playlist__submit {
  background: #f1f1f1;
  color: #0f0f0f;
  border: none;
  border-radius: 8px;
  padding: 0.5rem 0.9rem;
  font-weight: 600;
  cursor: pointer;
}
.new-playlist__submit:disabled {
  opacity: 0.5;
  cursor: default;
}
.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}
.state {
  padding: 1rem 0;
  opacity: 0.7;
}
.state--error {
  color: #ff6b6b;
}
</style>
