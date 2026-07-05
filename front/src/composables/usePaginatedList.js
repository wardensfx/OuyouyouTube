import { ref } from 'vue'

/**
 * Chargement paginé générique : première page + pages suivantes (scroll
 * infini), état loading/loadingMore/error cohérent, sans dupliquer cette
 * logique dans chaque vue (Trending/Channel/Search/PlaylistDetail).
 *
 * `fetchPage(pageToken)` doit renvoyer `{ items, next_page_token }` — le
 * format déjà utilisé par tous les endpoints paginés de l'API.
 */
export function usePaginatedList(fetchPage) {
  const items = ref([])
  const loading = ref(false)
  const loadingMore = ref(false)
  const error = ref(null)
  // Erreur de page suivante séparée de `error` (chargement initial) : un
  // échec de scroll infini ne doit pas remplacer toute la grille déjà
  // affichée par un état d'erreur plein écran.
  const loadMoreError = ref(null)
  const nextPageToken = ref(null)

  async function load() {
    loading.value = true
    error.value = null
    try {
      const page = await fetchPage()
      items.value = page.items
      nextPageToken.value = page.next_page_token
      return page.items
    } catch (e) {
      error.value = e.message
      return []
    } finally {
      loading.value = false
    }
  }

  async function loadMore() {
    if (!nextPageToken.value || loadingMore.value) return []
    loadingMore.value = true
    loadMoreError.value = null
    try {
      const page = await fetchPage(nextPageToken.value)
      items.value = [...items.value, ...page.items]
      nextPageToken.value = page.next_page_token
      return page.items
    } catch (e) {
      loadMoreError.value = e.message
      return []
    } finally {
      loadingMore.value = false
    }
  }

  return { items, loading, loadingMore, error, loadMoreError, nextPageToken, load, loadMore }
}
