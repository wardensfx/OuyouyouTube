<script setup>
import { ref, watch, onMounted, onActivated, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api/client'
import { useProgressStore } from '../stores/progress'
import { usePaginatedList } from '../composables/usePaginatedList'
import { useInfiniteScroll } from '../composables/useInfiniteScroll'
import VideoCard from '../components/VideoCard.vue'
import AddToPlaylistModal from '../components/AddToPlaylistModal.vue'
import SkeletonCard from '../components/SkeletonCard.vue'
import EmptyState from '../components/EmptyState.vue'
import LoadMoreStatus from '../components/LoadMoreStatus.vue'

defineOptions({ name: 'Search' })
const SKELETON_COUNT = 6

const progressStore = useProgressStore()

const props = defineProps({ q: { type: String, default: '' } })
const router = useRouter()

const term = ref(props.q)
const modalVideo = ref(null)
const searched = ref(false)
const inputEl = ref(null)

function focusInput() {
  nextTick(() => inputEl.value?.focus())
}
onMounted(focusInput)
onActivated(focusInput)

const {
  items: results,
  loading,
  loadingMore,
  error,
  loadMoreError,
  nextPageToken,
  load,
  loadMore,
} = usePaginatedList((pageToken) => api.search(term.value.trim(), pageToken))

async function runSearch(q) {
  if (!q.trim()) return
  searched.value = true
  progressStore.fetchFor((await load()).map((v) => v.video_id))
}

async function loadMoreWithProgress() {
  if (!term.value.trim()) return
  progressStore.fetchFor((await loadMore()).map((v) => v.video_id))
}
const { sentinel } = useInfiniteScroll(loadMoreWithProgress)

function submit() {
  router.push({ name: 'search', query: { q: term.value } })
}

watch(
  () => props.q,
  (q) => {
    term.value = q
    if (q) runSearch(q)
  },
  { immediate: true },
)
</script>

<template>
  <div class="search">
    <form class="search__bar" @submit.prevent="submit">
      <input ref="inputEl" v-model="term" type="search" placeholder="Rechercher…" class="search__input" />
      <button type="submit" class="search__submit">Rechercher</button>
    </form>

    <div v-if="loading" class="grid">
      <SkeletonCard v-for="n in SKELETON_COUNT" :key="n" />
    </div>
    <div v-else-if="error" class="state state--error">
      <p>{{ error }}</p>
      <button class="retry-btn" @click="runSearch(term)">Réessayer</button>
    </div>
    <EmptyState v-else-if="searched && !results.length" message="Aucun résultat." />

    <template v-else>
      <div class="grid">
        <VideoCard
          v-for="v in results"
          :key="v.video_id"
          :video="v"
          @add-to-playlist="modalVideo = v"
        />
      </div>
      <div v-if="nextPageToken" ref="sentinel" class="sentinel" />
      <LoadMoreStatus :loading="loadingMore" :error="loadMoreError" @retry="loadMoreWithProgress" />
    </template>

    <AddToPlaylistModal v-if="modalVideo" :video="modalVideo" @close="modalVideo = null" />
  </div>
</template>

<style scoped>
.search {
  padding: 1rem;
}
.search__bar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.search__input {
  flex: 1;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-sm);
  padding: 0.6rem 0.75rem;
  color: inherit;
  /* iOS Safari zoome automatiquement la page au focus d'un champ dont la
     taille de police calculée est < 16px — jamais en dessous de 1rem. */
  font-size: 1rem;
}
.search__submit {
  background: var(--accent-strong);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  padding: 0.6rem 1rem;
  font-weight: 600;
  cursor: pointer;
}
.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}
.sentinel {
  height: 1px;
}
.state {
  opacity: 0.7;
  padding: 1rem 0;
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
</style>
