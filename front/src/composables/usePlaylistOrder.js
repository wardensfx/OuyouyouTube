import { ref, computed, watch } from 'vue'

// YouTube Data API ne propose pas d'ordre personnalisé pour "mes playlists"
// (playlists.list ne le persiste pas) — c'est donc une préférence locale,
// comme l'ordre des sections de l'accueil.
const KEY = 'playlist_order_v1'

function load() {
  try {
    const raw = JSON.parse(localStorage.getItem(KEY))
    return Array.isArray(raw) ? raw : []
  } catch {
    return []
  }
}

function save(order) {
  localStorage.setItem(KEY, JSON.stringify(order))
}

export function usePlaylistOrder(getList) {
  const orderedIds = ref([])

  watch(
    getList,
    (list) => {
      const current = list || []
      const stored = load()
      const known = stored.filter((id) => current.some((p) => p.id === id))
      const extra = current.filter((p) => !stored.includes(p.id)).map((p) => p.id)
      orderedIds.value = [...known, ...extra]
    },
    { immediate: true },
  )

  const ordered = computed(() =>
    orderedIds.value.map((id) => (getList() || []).find((p) => p.id === id)).filter(Boolean),
  )

  function move(id, dir) {
    const arr = [...orderedIds.value]
    const idx = arr.indexOf(id)
    const target = idx + dir
    if (idx === -1 || target < 0 || target >= arr.length) return
    ;[arr[idx], arr[target]] = [arr[target], arr[idx]]
    orderedIds.value = arr
    save(arr)
  }

  return { ordered, move }
}
