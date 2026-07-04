/**
 * Client HTTP minimal. `credentials: 'include'` est indispensable pour que
 * le cookie de session (httponly) parte avec chaque requête vers le backend.
 */
async function request(path, options = {}) {
  const res = await fetch(path, {
    credentials: 'include',
    ...options,
  })
  if (res.status === 401) {
    window.location.href = '/auth/login'
    return
  }
  if (!res.ok) {
    const body = await res.text()
    throw new Error(`${res.status} ${res.statusText}: ${body}`)
  }
  const contentType = res.headers.get('content-type') || ''
  return contentType.includes('application/json') ? res.json() : res
}

export const api = {
  getPlaylists: () => request('/playlists'),
  getPlaylistItems: (playlistId) => request(`/playlists/${playlistId}/items`),
  getFavorites: () => request('/favorites'),

  prepareVideo: (videoId) => request(`/video/${videoId}/prepare`, { method: 'POST' }),
  getVideoStatus: (videoId) => request(`/video/${videoId}/status`),
  streamUrl: (videoId) => `/video/${videoId}/stream`,

  getAccounts: () => request('/auth/accounts'),
  activateAccount: (accountId) => request(`/auth/accounts/${accountId}/activate`, { method: 'POST' }),
  unlinkAccount: (accountId) => request(`/auth/accounts/${accountId}`, { method: 'DELETE' }),
  loginUrl: ({ link = false } = {}) => `/auth/login${link ? '?link=true' : ''}`,
  logout: () => request('/auth/logout', { method: 'POST' }),
}
