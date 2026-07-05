import { onUnmounted, ref, watch } from 'vue'

/**
 * Déclenche `onIntersect` quand l'élément lié à `sentinel` (un div vide en
 * bas de grille, rendu tant qu'il reste une page à charger) entre dans le
 * viewport. IntersectionObserver natif plutôt qu'un listener de scroll —
 * pas de calcul manuel de position, pas de throttle à gérer nous-mêmes.
 */
export function useInfiniteScroll(onIntersect) {
  const sentinel = ref(null)
  let observer = null

  watch(sentinel, (el, _prev, onCleanup) => {
    if (!el) return
    observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) onIntersect()
      },
      { rootMargin: '400px' },
    )
    observer.observe(el)
    onCleanup(() => observer?.disconnect())
  })

  onUnmounted(() => observer?.disconnect())

  return { sentinel }
}
