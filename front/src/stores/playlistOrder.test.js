import 'fake-indexeddb/auto'
import { openDB } from 'idb'
import { describe, it, expect, beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { usePlaylistOrderStore } from './playlistOrder'

describe('usePlaylistOrderStore', () => {
  beforeEach(async () => {
    setActivePinia(createPinia())
    // db/index.js memoizes its IndexedDB connection at module scope, so it
    // survives across tests in this file — clear its data directly (via an
    // independent connection to the same database) for real test isolation.
    const db = await openDB('ouyouyoutube', 2, {
      upgrade(db) {
        for (const name of ['playlist_order', 'history']) {
          if (!db.objectStoreNames.contains(name)) db.createObjectStore(name, { keyPath: 'key' })
        }
      },
    })
    await db.clear('playlist_order')
    db.close()
  })

  it('starts empty and appends unknown playlists on sync', async () => {
    const store = usePlaylistOrderStore()
    await store.sync([{ id: 'p1' }, { id: 'p2' }])
    expect(store.ids).toEqual(['p1', 'p2'])
  })

  it('keeps known order and appends only new playlists', async () => {
    const store = usePlaylistOrderStore()
    await store.sync([{ id: 'p1' }, { id: 'p2' }])
    store.ids = ['p2', 'p1']
    await store.sync([{ id: 'p1' }, { id: 'p2' }, { id: 'p3' }])
    expect(store.ids).toEqual(['p2', 'p1', 'p3'])
  })

  it('drops playlists that no longer exist', async () => {
    const store = usePlaylistOrderStore()
    await store.sync([{ id: 'p1' }, { id: 'p2' }])
    await store.sync([{ id: 'p2' }])
    expect(store.ids).toEqual(['p2'])
  })

  it('move() swaps adjacent ids and persists them', async () => {
    const store = usePlaylistOrderStore()
    await store.sync([{ id: 'p1' }, { id: 'p2' }])
    await store.move('p1', 1)
    expect(store.ids).toEqual(['p2', 'p1'])

    // A fresh store instance (simulating a reload) should read the
    // persisted order back from IndexedDB instead of starting empty.
    setActivePinia(createPinia())
    const reloaded = usePlaylistOrderStore()
    await reloaded._ensureLoaded()
    expect(reloaded.ids).toEqual(['p2', 'p1'])
  })

  it('move() is a no-op out of bounds', async () => {
    const store = usePlaylistOrderStore()
    await store.sync([{ id: 'p1' }, { id: 'p2' }])
    store.move('p1', -1)
    expect(store.ids).toEqual(['p1', 'p2'])
    store.move('missing', 1)
    expect(store.ids).toEqual(['p1', 'p2'])
  })
})
