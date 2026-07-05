import { computed, ref, watch } from 'vue'
import { useLibraryStore } from '../stores/library'

// Toggle + animation de pulse + garde anti-double-clic pour le bouton
// Like, partagés entre VideoCard.vue (grilles) et Player.vue (sous le
// lecteur) pour ne pas dupliquer cette logique.
export function useLikeButton(getVideo) {
  const library = useLibraryStore()
  const pending = ref(false)
  const pulsing = ref(false)
  // État local après un toggle : prime sur tout le reste tant qu'on reste
  // sur la même vidéo, pour ne pas dépendre d'un re-fetch pour refléter
  // l'action qu'on vient de faire. Remis à zéro dès que la vidéo change
  // (cf. watch plus bas), sinon l'état togglé d'une vidéo fuiterait sur la
  // suivante affichée par la même instance du composable (Player.vue garde
  // la même instance en changeant de vidéo).
  const override = ref(null)

  watch(
    () => getVideo()?.video_id,
    () => {
      override.value = null
    },
  )

  const liked = computed(() => {
    const video = getVideo()
    if (!video) return false
    if (override.value !== null) return override.value
    // `video.liked` (renvoyé par /api/video/{id}/info via videos.getRating,
    // cf. #87) est la source de vérité pour une vidéo précise. Le repli sur
    // library.favorites ne concerne que VideoCard.vue dans Liked.vue, où
    // chaque carte vient déjà de library.favorites — donc toujours exact là,
    // y compris avec la pagination des favoris (#78), sans appel réseau
    // supplémentaire par carte.
    if (typeof video.liked === 'boolean') return video.liked
    return library.favorites.some((v) => v.video_id === video.video_id)
  })

  async function toggleLike() {
    const video = getVideo()
    if (!video || pending.value) return
    pending.value = true
    pulsing.value = true
    setTimeout(() => (pulsing.value = false), 300)
    const next = !liked.value
    try {
      if (liked.value) await library.unlikeVideo(video.video_id)
      else await library.likeVideo(video)
      override.value = next
    } finally {
      pending.value = false
    }
  }

  return { liked, pending, pulsing, toggleLike }
}
