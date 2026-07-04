<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api/client'
import VideoCard from '../components/VideoCard.vue'
import AddToPlaylistModal from '../components/AddToPlaylistModal.vue'

defineOptions({ name: 'Search' })

const props = defineProps({ q: { type: String, default: '' } })
const router = useRouter()

const term = ref(props.q)
const results = ref([])
const loading = ref(false)
const error = ref(null)
const modalVideo = ref(null)
const searched = ref(false)

async function runSearch(q) {
  if (!q.trim()) return
  loading.value = true
  error.value = null
  searched.value = true
  try {
    results.value = await api.search(q.trim())
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

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
      <input v-model="term" type="search" placeholder="Rechercher…" class="search__input" />
      <button type="submit" class="search__submit">Rechercher</button>
    </form>

    <p v-if="loading" class="state">Recherche…</p>
    <p v-else-if="error" class="state state--error">{{ error }}</p>
    <p v-else-if="searched && !results.length" class="state">Aucun résultat.</p>

    <div v-else class="grid">
      <VideoCard
        v-for="v in results"
        :key="v.video_id"
        :video="v"
        @add-to-playlist="modalVideo = v"
      />
    </div>

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
  font-size: 0.95rem;
}
.search__submit {
  background: var(--accent);
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
.state {
  opacity: 0.7;
  padding: 1rem 0;
}
.state--error {
  color: var(--danger);
}
</style>
