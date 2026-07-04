import { computed, watch } from 'vue'
import { usePlaylistOrderStore } from '../stores/playlistOrder'

export function usePlaylistOrder(getList) {
  const store = usePlaylistOrderStore()

  watch(getList, (list) => store.sync(list || []), { immediate: true })

  const ordered = computed(() =>
    store.ids.map((id) => (getList() || []).find((p) => p.id === id)).filter(Boolean),
  )

  return { ordered, move: store.move }
}
