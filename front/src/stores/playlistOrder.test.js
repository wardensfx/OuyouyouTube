import 'fake-indexeddb/auto'
import { openDB } from 'idb'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { DB_VERSION, STORES, dbNameFor } from '../db'
import { usePlaylistOrderStore } from './playlistOrder'

// db/index.js resolves the active account via the API to scope the
// database per account (see #56) — stub a single fixed active account so
// tests don't depend on a real backend.
vi.mock('../api/client', () => ({
  api: { getAccounts: () => Promise.resolve([{ id: 'test-account', active: true }]) },
}))

describe('usePlaylistOrderStore', () => {
  beforeEach(async () => {
    setActivePinia(createPinia())
    // db/index.js memoizes its IndexedDB connection at module scope, so it
    // survives across tests in this file — clear its data directly (via an
    // independent connection to the same database) for real test isolation.
    const db = await openDB(dbNameFor('test-account'), DB_VERSION, {
      upgrade(db) {
        for (const name of STORES) {
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
    await store.move('p1', -1)
    expect(store.ids).toEqual(['p1', 'p2'])
    await store.move('missing', 1)
    expect(store.ids).toEqual(['p1', 'p2'])
  })

  it('move() called before the initial load resolves is not silently lost', async () => {
    // Regression test for #54: move() now awaits _ensureLoaded() first,
    // so a call racing the initial IndexedDB read no longer gets dropped
    // (and then clobbered when the pending load resolves afterwards).
    const db = await openDB(dbNameFor('test-account'), DB_VERSION, {
      upgrade(db) {
        for (const name of STORES) {
          if (!db.objectStoreNames.contains(name)) db.createObjectStore(name, { keyPath: 'key' })
        }
      },
    })
    await db.put('playlist_order', { key: 'ids', value: ['p1', 'p2'] })
    db.close()

    const store = usePlaylistOrderStore()
    // No await here on purpose: fire move() immediately, before the
    // store's own lazy load has had a chance to resolve.
    const movePromise = store.move('p1', 1)
    await movePromise
    expect(store.ids).toEqual(['p2', 'p1'])
  })
})
