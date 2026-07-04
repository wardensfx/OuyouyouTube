/**
 * Client HTTP minimal. `credentials: 'include'` est indispensable pour que
 * le cookie de session (httponly) parte avec chaque requête vers le backend.
 * Tous les endpoints backend vivent sous /api pour ne jamais entrer en
 * collision avec les routes du front (ex. /search, /playlists/manage).
 */
const API_BASE = '/api'

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: 'include',
    ...options,
  })
  if (res.status === 401) {
    window.location.href = `${API_BASE}/auth/login`
    return
  }
  if (!res.ok) {
    const body = await res.text()
    throw new Error(`${res.status} ${res.statusText}: ${body}`)
  }
  const contentType = res.headers.get('content-type') || ''
  return contentType.includes('application/json') ? res.json() : res
}

function jsonBody(body) {
  return { headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }
}

export const api = {
  getPlaylists: () => request('/playlists'),
  createPlaylist: (title) => request('/playlists', { method: 'POST', ...jsonBody({ title }) }),
  renamePlaylist: (playlistId, title) =>
    request(`/playlists/${playlistId}`, { method: 'PATCH', ...jsonBody({ title }) }),
  deletePlaylist: (playlistId) => request(`/playlists/${playlistId}`, { method: 'DELETE' }),
  getPlaylistItems: (playlistId) => request(`/playlists/${playlistId}/items`),
  addPlaylistItem: (playlistId, videoId) =>
    request(`/playlists/${playlistId}/items`, { method: 'POST', ...jsonBody({ video_id: videoId }) }),
  removePlaylistItem: (playlistId, itemId) =>
    request(`/playlists/${playlistId}/items/${itemId}`, { method: 'DELETE' }),
  getFavorites: () => request('/favorites'),
  likeVideo: (videoId) => request(`/favorites/${videoId}`, { method: 'PUT' }),
  unlikeVideo: (videoId) => request(`/favorites/${videoId}`, { method: 'DELETE' }),

  search: (q) => request(`/search?q=${encodeURIComponent(q)}`),

  getTrending: () => request('/home/trending'),
  getSubscriptionsFeed: () => request('/home/subscriptions'),

  getVideoInfo: (videoId) => request(`/video/${videoId}/info`),
  prepareVideo: (videoId) => request(`/video/${videoId}/prepare`, { method: 'POST' }),
  getVideoStatus: (videoId) => request(`/video/${videoId}/status`),
  streamUrl: (videoId) => `${API_BASE}/video/${videoId}/stream`,

  getAccounts: () => request('/auth/accounts'),
  activateAccount: (accountId) => request(`/auth/accounts/${accountId}/activate`, { method: 'POST' }),
  unlinkAccount: (accountId) => request(`/auth/accounts/${accountId}`, { method: 'DELETE' }),
  avatarUrl: (accountId) => `${API_BASE}/auth/accounts/${accountId}/avatar`,
  loginUrl: ({ link = false } = {}) => `${API_BASE}/auth/login${link ? '?link=true' : ''}`,
  logout: () => request('/auth/logout', { method: 'POST' }),
}
