const UNITS = [
  ['an', 60 * 60 * 24 * 365],
  ['mois', 60 * 60 * 24 * 30],
  ['semaine', 60 * 60 * 24 * 7],
  ['jour', 60 * 60 * 24],
  ['heure', 60 * 60],
  ['minute', 60],
]

export function formatRelativeDate(iso) {
  if (!iso) return ''
  const diffSec = Math.floor((Date.now() - new Date(iso).getTime()) / 1000)
  if (diffSec < 60) return "à l'instant"

  for (const [label, secs] of UNITS) {
    const value = Math.floor(diffSec / secs)
    if (value >= 1) {
      const plural = value > 1 && label !== 'mois' ? 's' : ''
      return `il y a ${value} ${label}${plural}`
    }
  }
  return "à l'instant"
}

export function formatDuration(iso) {
  if (!iso) return null
  const match = /^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$/.exec(iso)
  if (!match) return null
  const hours = Number(match[1] || 0)
  const minutes = Number(match[2] || 0)
  const seconds = Number(match[3] || 0)
  const pad = (n) => String(n).padStart(2, '0')
  if (hours) return `${hours}:${pad(minutes)}:${pad(seconds)}`
  return `${minutes}:${pad(seconds)}`
}

export function formatViewCount(count) {
  const n = Number(count)
  if (!n) return null
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1).replace(/\.0$/, '')} M de vues`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1).replace(/\.0$/, '')} k vues`
  return `${n} vue${n > 1 ? 's' : ''}`
}
