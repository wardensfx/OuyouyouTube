<script setup>
import { onMounted, ref } from 'vue'
import { Settings, ChevronUp, ChevronDown, Plus } from '@lucide/vue'
import { api } from '../api/client'
import { useLibraryStore } from '../stores/library'
import VideoCard from '../components/VideoCard.vue'
import PlaylistCard from '../components/PlaylistCard.vue'
import AddToPlaylistModal from '../components/AddToPlaylistModal.vue'

defineOptions({ name: 'Home' })

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

// Accueil personnalisable : ordre + visibilité des sections, persistés en
// local (préférence d'appareil, pas besoin de synchro serveur pour ça).
const SECTION_LABELS = {
  subscriptions: 'Abonnements',
  trending: 'Tendances',
  playlists: 'Playlists',
  favorites: 'Favoris',
}
const DEFAULT_ORDER = Object.keys(SECTION_LABELS)
const PREFS_KEY = 'home_sections_v1'

function loadPrefs() {
  try {
    const parsed = JSON.parse(localStorage.getItem(PREFS_KEY))
    const order = (parsed?.order || []).filter((k) => DEFAULT_ORDER.includes(k))
    for (const k of DEFAULT_ORDER) if (!order.includes(k)) order.push(k)
    return { order, hidden: Array.isArray(parsed?.hidden) ? parsed.hidden : [] }
  } catch {
    return { order: [...DEFAULT_ORDER], hidden: [] }
  }
}

const prefs = ref(loadPrefs())
const settingsOpen = ref(false)

function savePrefs() {
  localStorage.setItem(PREFS_KEY, JSON.stringify(prefs.value))
}
function orderIndex(key) {
  return prefs.value.order.indexOf(key)
}
function isHidden(key) {
  return prefs.value.hidden.includes(key)
}
function toggleHidden(key) {
  const i = prefs.value.hidden.indexOf(key)
  if (i === -1) prefs.value.hidden.push(key)
  else prefs.value.hidden.splice(i, 1)
  savePrefs()
}
function move(key, dir) {
  const arr = prefs.value.order
  const idx = arr.indexOf(key)
  const target = idx + dir
  if (target < 0 || target >= arr.length) return
  ;[arr[idx], arr[target]] = [arr[target], arr[idx]]
  savePrefs()
}
</script>

<template>
  <div class="home">
    <header class="home__header">
      <h1>Accueil</h1>
      <button class="link-button" @click="settingsOpen = !settingsOpen"><Settings :size="16" /> Personnaliser</button>
    </header>

    <div v-if="settingsOpen" class="home-settings__backdrop" @click="settingsOpen = false" />
    <div v-if="settingsOpen" class="home-settings glass">
      <div v-for="key in prefs.order" :key="key" class="home-settings__row">
        <label class="home-settings__label">
          <input type="checkbox" :checked="!isHidden(key)" @change="toggleHidden(key)" />
          {{ SECTION_LABELS[key] }}
        </label>
        <div class="home-settings__buttons">
          <button :disabled="orderIndex(key) === 0" @click="move(key, -1)"><ChevronUp :size="16" /></button>
          <button :disabled="orderIndex(key) === prefs.order.length - 1" @click="move(key, 1)"><ChevronDown :size="16" /></button>
        </div>
      </div>
    </div>

    <div class="home__sections">
      <section v-show="!isHidden('subscriptions')" class="section" :style="{ order: orderIndex('subscriptions') }">
        <h2>Abonnements</h2>
        <p v-if="subscriptionsLoading" class="state">Chargement…</p>
        <p v-else-if="subscriptionsError" class="state state--error">{{ subscriptionsError }}</p>
        <p v-else-if="!subscriptions.length" class="state">Rien de nouveau pour l'instant.</p>
        <div v-else class="grid">
          <VideoCard
            v-for="v in subscriptions"
            :key="v.video_id"
            :video="v"
            @add-to-playlist="modalVideo = v"
          />
        </div>
      </section>

      <section v-show="!isHidden('trending')" class="section" :style="{ order: orderIndex('trending') }">
        <h2>Tendances</h2>
        <p v-if="trendingLoading" class="state">Chargement…</p>
        <p v-else-if="trendingError" class="state state--error">{{ trendingError }}</p>
        <div v-else class="grid">
          <VideoCard
            v-for="v in trending"
            :key="v.video_id"
            :video="v"
            @add-to-playlist="modalVideo = v"
          />
        </div>
      </section>

      <section v-show="!isHidden('playlists')" class="section" :style="{ order: orderIndex('playlists') }">
        <div class="section__header">
          <h2>Playlists</h2>
          <button class="link-button" @click="creating = !creating"><Plus :size="16" /> Nouvelle</button>
        </div>

        <p v-if="library.loading" class="state">Chargement…</p>
        <p v-else-if="library.error" class="state state--error">{{ library.error }}</p>
        <template v-else>
          <form v-if="creating" class="new-playlist" @submit.prevent="submitNewPlaylist">
            <input v-model="newPlaylistTitle" type="text" placeholder="Titre de la playlist…" class="new-playlist__input" />
            <button type="submit" class="new-playlist__submit" :disabled="!newPlaylistTitle.trim()">Créer</button>
          </form>

          <TransitionGroup tag="div" name="grid" class="grid">
            <PlaylistCard v-for="p in library.playlists" :key="p.id" :playlist="p" />
          </TransitionGroup>
        </template>
      </section>

      <section v-show="!isHidden('favorites')" class="section" :style="{ order: orderIndex('favorites') }">
        <h2>Favoris</h2>
        <p v-if="library.loading" class="state">Chargement…</p>
        <p v-else-if="library.error" class="state state--error">{{ library.error }}</p>
        <TransitionGroup v-else tag="div" name="grid" class="grid">
          <VideoCard
            v-for="v in library.favorites"
            :key="v.video_id"
            :video="v"
            :show-like="false"
            @add-to-playlist="modalVideo = v"
          />
        </TransitionGroup>
      </section>
    </div>

    <AddToPlaylistModal v-if="modalVideo" :video="modalVideo" @close="modalVideo = null" />
  </div>
</template>

<style scoped>
.home__header {
  padding: 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.home-settings__backdrop {
  position: fixed;
  inset: 0;
  z-index: 20;
}
.home-settings {
  position: relative;
  z-index: 21;
  margin: 0 1rem 1rem;
  padding: 0.75rem;
  border-radius: var(--radius-lg);
}
.home-settings__row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.4rem 0.25rem;
}
.home-settings__label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}
.home-settings__buttons {
  display: flex;
  gap: 0.3rem;
}
.home-settings__buttons button {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid var(--glass-border);
  color: inherit;
  border-radius: var(--radius-sm);
  width: 28px;
  height: 28px;
  cursor: pointer;
}
.home-settings__buttons button:disabled {
  opacity: 0.3;
  cursor: default;
}
.home__sections {
  display: flex;
  flex-direction: column;
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
  display: flex;
  align-items: center;
  gap: 0.35rem;
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
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-sm);
  padding: 0.5rem;
  color: inherit;
}
.new-playlist__submit {
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
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
  padding: 1rem 0;
  opacity: 0.7;
}
.state--error {
  color: var(--danger);
}
</style>
