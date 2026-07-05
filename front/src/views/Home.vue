<script setup>
import { computed, onMounted, ref } from 'vue'
import { Settings, ChevronUp, ChevronDown, Plus, ChevronRight, Heart, ListMusic } from '@lucide/vue'
import { api } from '../api/client'
import { useLibraryStore } from '../stores/library'
import { useProgressStore } from '../stores/progress'
import { usePlaylistOrder } from '../composables/usePlaylistOrder'
import VideoCard from '../components/VideoCard.vue'
import PlaylistCard from '../components/PlaylistCard.vue'
import AddToPlaylistModal from '../components/AddToPlaylistModal.vue'
import SkeletonCard from '../components/SkeletonCard.vue'
import EmptyState from '../components/EmptyState.vue'
import PullToRefresh from '../components/PullToRefresh.vue'

defineOptions({ name: 'Home' })

const PREVIEW_COUNT = 6

const library = useLibraryStore()
const progressStore = useProgressStore()
onMounted(async () => {
  await library.loadAll()
  progressStore.fetchFor(library.favorites.map((v) => v.video_id))
})

const { ordered: orderedPlaylists } = usePlaylistOrder(() => library.playlists)
const playlistsPreview = computed(() => orderedPlaylists.value.slice(0, PREVIEW_COUNT))
const favoritesPreview = computed(() => library.favorites.slice(0, PREVIEW_COUNT))

const modalVideo = ref(null)
const creating = ref(false)
const newPlaylistTitle = ref('')

async function submitNewPlaylist() {
  if (!newPlaylistTitle.value.trim()) return
  await library.createPlaylist(newPlaylistTitle.value.trim())
  newPlaylistTitle.value = ''
  creating.value = false
}

// Les vidéos vues sortent des flux de découverte (Abonnements/Tendances) —
// mais pas des Favoris/Playlists, qui restent des listes qu'on constitue
// soi-même et où on doit pouvoir retrouver une vidéo déjà vue.
function notWatched(v) {
  return !progressStore.items[v.video_id]?.watched
}

const subscriptions = ref([])
const subscriptionsLoading = ref(false)
const subscriptionsError = ref(null)
const subscriptionsVisible = computed(() => subscriptions.value.filter(notWatched))
const subscriptionsPreview = computed(() => subscriptionsVisible.value.slice(0, PREVIEW_COUNT))

const trending = ref([])
const trendingLoading = ref(false)
const trendingError = ref(null)
const trendingVisible = computed(() => trending.value.filter(notWatched))
const trendingPreview = computed(() => trendingVisible.value.slice(0, PREVIEW_COUNT))

async function loadSubscriptions() {
  subscriptionsLoading.value = true
  subscriptionsError.value = null
  try {
    subscriptions.value = await api.getSubscriptionsFeed()
    progressStore.fetchFor(subscriptions.value.map((v) => v.video_id))
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
    // Aperçu limité à PREVIEW_COUNT : la première page suffit, pas besoin
    // de pagination ici (voir Trending.vue pour la liste complète).
    trending.value = (await api.getTrending()).items
    progressStore.fetchFor(trending.value.map((v) => v.video_id))
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

async function refreshAll() {
  await Promise.all([library.loadAll(), loadSubscriptions(), loadTrending()])
  progressStore.fetchFor([
    ...library.favorites.map((v) => v.video_id),
    ...subscriptions.value.map((v) => v.video_id),
    ...trending.value.map((v) => v.video_id),
  ])
}

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
  <PullToRefresh class="home" :refresh="refreshAll">
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
          <button title="Monter" :disabled="orderIndex(key) === 0" @click="move(key, -1)"><ChevronUp :size="16" /></button>
          <button
            title="Descendre"
            :disabled="orderIndex(key) === prefs.order.length - 1"
            @click="move(key, 1)"
          ><ChevronDown :size="16" /></button>
        </div>
      </div>
    </div>

    <div class="home__sections">
      <section v-show="!isHidden('subscriptions')" class="section" :style="{ order: orderIndex('subscriptions') }">
        <div class="section__header">
          <h2>Abonnements</h2>
          <RouterLink to="/subscriptions" class="link-button">Voir tout <ChevronRight :size="16" /></RouterLink>
        </div>
        <div v-if="subscriptionsLoading" class="grid">
          <SkeletonCard v-for="n in PREVIEW_COUNT" :key="n" />
        </div>
        <p v-else-if="subscriptionsError" class="state state--error">{{ subscriptionsError }}</p>
        <EmptyState v-else-if="!subscriptionsVisible.length" message="Rien de nouveau pour l'instant." />
        <div v-else class="grid">
          <VideoCard
            v-for="v in subscriptionsPreview"
            :key="v.video_id"
            :video="v"
            @add-to-playlist="modalVideo = v"
          />
        </div>
      </section>

      <section v-show="!isHidden('trending')" class="section" :style="{ order: orderIndex('trending') }">
        <div class="section__header">
          <h2>Tendances</h2>
          <RouterLink to="/trending" class="link-button">Voir tout <ChevronRight :size="16" /></RouterLink>
        </div>
        <div v-if="trendingLoading" class="grid">
          <SkeletonCard v-for="n in PREVIEW_COUNT" :key="n" />
        </div>
        <p v-else-if="trendingError" class="state state--error">{{ trendingError }}</p>
        <EmptyState v-else-if="!trendingVisible.length" message="Rien à afficher pour l'instant." />
        <div v-else class="grid">
          <VideoCard
            v-for="v in trendingPreview"
            :key="v.video_id"
            :video="v"
            @add-to-playlist="modalVideo = v"
          />
        </div>
      </section>

      <section v-show="!isHidden('playlists')" class="section" :style="{ order: orderIndex('playlists') }">
        <div class="section__header">
          <h2>Playlists</h2>
          <div class="section__header-actions">
            <button class="link-button" @click="creating = !creating"><Plus :size="16" /> Nouvelle</button>
            <RouterLink to="/playlists/manage" class="link-button">Voir tout <ChevronRight :size="16" /></RouterLink>
          </div>
        </div>

        <div v-if="library.loading" class="grid">
          <SkeletonCard v-for="n in PREVIEW_COUNT" :key="n" />
        </div>
        <p v-else-if="library.error" class="state state--error">{{ library.error }}</p>
        <template v-else>
          <form v-if="creating" class="new-playlist" @submit.prevent="submitNewPlaylist">
            <input v-model="newPlaylistTitle" type="text" placeholder="Titre de la playlist…" class="new-playlist__input" />
            <button type="submit" class="new-playlist__submit" :disabled="!newPlaylistTitle.trim()">Créer</button>
          </form>

          <EmptyState v-if="!playlistsPreview.length" :icon="ListMusic" message="Aucune playlist pour l'instant." />
          <TransitionGroup v-else tag="div" name="grid" class="grid">
            <PlaylistCard v-for="p in playlistsPreview" :key="p.id" :playlist="p" />
          </TransitionGroup>
        </template>
      </section>

      <section v-show="!isHidden('favorites')" class="section" :style="{ order: orderIndex('favorites') }">
        <div class="section__header">
          <h2>Favoris</h2>
          <RouterLink to="/favorites" class="link-button">Voir tout <ChevronRight :size="16" /></RouterLink>
        </div>
        <div v-if="library.loading" class="grid">
          <SkeletonCard v-for="n in PREVIEW_COUNT" :key="n" />
        </div>
        <p v-else-if="library.error" class="state state--error">{{ library.error }}</p>
        <EmptyState v-else-if="!favoritesPreview.length" :icon="Heart" message="Aucun favori pour l'instant." />
        <TransitionGroup v-else tag="div" name="grid" class="grid">
          <VideoCard
            v-for="v in favoritesPreview"
            :key="v.video_id"
            :video="v"
            @add-to-playlist="modalVideo = v"
          />
        </TransitionGroup>
      </section>
    </div>

    <AddToPlaylistModal v-if="modalVideo" :video="modalVideo" @close="modalVideo = null" />
  </PullToRefresh>
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
  position: relative;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid var(--glass-border);
  color: inherit;
  border-radius: var(--radius-sm);
  width: 28px;
  height: 28px;
  cursor: pointer;
}
/* Élargit la zone tactile sans agrandir le rendu visuel (cf. #93) : boutons
   serrés l'un contre l'autre à l'horizontale (gap 0.3rem = 4.8px), donc
   l'agrandissement horizontal reste modéré. */
.home-settings__buttons button::before {
  content: '';
  position: absolute;
  inset: -8px -2px;
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
.section__header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.section h2 {
  font-size: 1rem;
  opacity: 0.7;
  margin: 0;
}
.link-button {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  background: transparent;
  border: none;
  color: inherit;
  opacity: 0.8;
  font-size: 0.85rem;
  cursor: pointer;
  text-decoration: none;
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
  background: var(--accent-strong);
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
