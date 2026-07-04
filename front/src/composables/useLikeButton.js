import { computed, ref } from 'vue'
import { useLibraryStore } from '../stores/library'

// Toggle + animation de pulse + garde anti-double-clic pour le bouton
// Like, partagés entre VideoCard.vue (grilles) et Player.vue (sous le
// lecteur) pour ne pas dupliquer cette logique.
export function useLikeButton(getVideo) {
  const library = useLibraryStore()
  const pending = ref(false)
  const pulsing = ref(false)

  const liked = computed(() => {
    const video = getVideo()
    return !!video && library.favorites.some((v) => v.video_id === video.video_id)
  })

  async function toggleLike() {
    const video = getVideo()
    if (!video || pending.value) return
    pending.value = true
    pulsing.value = true
    setTimeout(() => (pulsing.value = false), 300)
    try {
      if (liked.value) await library.unlikeVideo(video.video_id)
      else await library.likeVideo(video)
    } finally {
      pending.value = false
    }
  }

  return { liked, pending, pulsing, toggleLike }
}
