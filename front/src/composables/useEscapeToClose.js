import { watch } from 'vue'

/**
 * Ferme un panneau/dialogue au clavier (Escape) — sans ça, un utilisateur
 * au clavier seul ou avec lecteur d'écran n'a aucun moyen de refermer une
 * modale/un menu qui ne se ferme qu'au clic sur le fond.
 */
export function useEscapeToClose(isOpen, onClose) {
  function handleKeydown(e) {
    if (e.key === 'Escape') onClose()
  }

  watch(
    isOpen,
    (open, _prev, onCleanup) => {
      if (!open) return
      window.addEventListener('keydown', handleKeydown)
      onCleanup(() => window.removeEventListener('keydown', handleKeydown))
    },
    { immediate: true },
  )
}
