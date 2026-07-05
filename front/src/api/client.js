/**
 * Client HTTP minimal. `credentials: 'include'` est indispensable pour que
 * le cookie de session (httponly) parte avec chaque requête vers le backend.
 * Tous les endpoints backend vivent sous /api pour ne jamais entrer en
 * collision avec les routes du front (ex. /search, /playlists/manage).
 */
const API_BASE = '/api'

// Sur session expirée, on redirige déjà vers /auth/login : ce type d'erreur
// sert seulement à ce que l'appelant sache qu'il ne recevra jamais de
// réponse, plutôt que de planter plus loin sur un `undefined` inattendu.
export class SessionExpiredError extends Error {
  constructor() {
    super('Session expirée, redirection…')
    this.name = 'SessionExpiredError'
  }
}

// Les erreurs FastAPI ({"detail": "..."}) sont déjà rédigées en français
// dans ce projet (ex. "Vidéo introuvable.") — les extraire donne un message
// précis sans repasser par le statut/texte HTTP brut en anglais. Le repli
// générique ne sert que pour les réponses qui n'ont pas cette forme (erreur
// réseau, page d'erreur générique d'un proxy, etc.).
function friendlyMessage(status, body) {
  try {
    const detail = JSON.parse(body)?.detail
    if (typeof detail === 'string' && detail) return detail
  } catch {
    // corps non-JSON : repli ci-dessous
  }
  if (status >= 500) return 'Erreur serveur, réessaie plus tard.'
  return 'Une erreur est survenue.'
}

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: 'include',
    ...options,
  })
  if (res.status === 401) {
    window.location.href = `${API_BASE}/auth/login`
    throw new SessionExpiredError()
  }
  if (!res.ok) {
    throw new Error(friendlyMessage(res.status, await res.text()))
  }
  const contentType = res.headers.get('content-type') || ''
  return contentType.includes('application/json') ? res.json() : res
}

function jsonBody(body) {
  return { headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }
}

// Petit helper pour les listes paginées (favoris, tendances, recherche,
// vidéos de chaîne) : ajoute ?page_token=... seulement s'il y en a un
// (première page = pas de token), sur une base de query déjà présente ou non.
function withPageToken(path, pageToken, hasQuery = false) {
  if (!pageToken) return path
  return `${path}${hasQuery ? '&' : '?'}page_token=${encodeURIComponent(pageToken)}`
}

export const api = {
  getPlaylists: () => request('/playlists'),
  createPlaylist: (title) => request('/playlists', { method: 'POST', ...jsonBody({ title }) }),
  renamePlaylist: (playlistId, title) =>
    request(`/playlists/${playlistId}`, { method: 'PATCH', ...jsonBody({ title }) }),
  deletePlaylist: (playlistId) => request(`/playlists/${playlistId}`, { method: 'DELETE' }),
  getPlaylistItems: (playlistId, pageToken) => request(withPageToken(`/playlists/${playlistId}/items`, pageToken)),
  addPlaylistItem: (playlistId, videoId) =>
    request(`/playlists/${playlistId}/items`, { method: 'POST', ...jsonBody({ video_id: videoId }) }),
  removePlaylistItem: (playlistId, itemId) =>
    request(`/playlists/${playlistId}/items/${itemId}`, { method: 'DELETE' }),
  getFavorites: (pageToken) => request(withPageToken('/favorites', pageToken)),
  likeVideo: (videoId) => request(`/favorites/${videoId}`, { method: 'PUT' }),
  unlikeVideo: (videoId) => request(`/favorites/${videoId}`, { method: 'DELETE' }),

  search: (q, pageToken) => request(withPageToken(`/search?q=${encodeURIComponent(q)}`, pageToken, true)),

  getTrending: (pageToken) => request(withPageToken('/home/trending', pageToken)),
  getSubscriptionsFeed: () => request('/home/subscriptions'),

  getVideoInfo: (videoId) => request(`/video/${videoId}/info`),
  getProgressBulk: (videoIds) => request(`/video/progress?ids=${videoIds.map(encodeURIComponent).join(',')}`),
  saveProgress: (videoId, position, duration) =>
    request(`/video/${videoId}/progress`, { method: 'PUT', ...jsonBody({ position, duration }) }),
  setWatched: (videoId, watched) =>
    request(`/video/${videoId}/watched`, { method: 'PUT', ...jsonBody({ watched }) }),
  prepareVideo: (videoId) => request(`/video/${videoId}/prepare`, { method: 'POST' }),
  getVideoStatus: (videoId) => request(`/video/${videoId}/status`),
  streamUrl: (videoId) => `${API_BASE}/video/${videoId}/stream`,

  getChannel: (channelId) => request(`/channels/${channelId}`),
  getChannelVideos: (channelId, pageToken) => request(withPageToken(`/channels/${channelId}/videos`, pageToken)),

  getAccounts: () => request('/auth/accounts'),
  activateAccount: (accountId) => request(`/auth/accounts/${accountId}/activate`, { method: 'POST' }),
  unlinkAccount: (accountId) => request(`/auth/accounts/${accountId}`, { method: 'DELETE' }),
  avatarUrl: (accountId) => `${API_BASE}/auth/accounts/${accountId}/avatar`,
  loginUrl: ({ link = false } = {}) => `${API_BASE}/auth/login${link ? '?link=true' : ''}`,
  logout: () => request('/auth/logout', { method: 'POST' }),
}
