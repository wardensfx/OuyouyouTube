import 'fake-indexeddb/auto'
import { openDB } from 'idb'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { reactive } from 'vue'
import { getValue, setValue, listValues, deleteValue, clearStore, DB_VERSION, STORES, dbNameFor } from './index'

// This module resolves the active account via the API to scope the
// database per account (see #56) — stub a single fixed active account so
// tests don't depend on a real backend.
vi.mock('../api/client', () => ({
  api: { getAccounts: () => Promise.resolve([{ id: 'test-account', active: true }]) },
}))

describe('db (IndexedDB wrapper)', () => {
  beforeEach(async () => {
    // The connection this module opens is memoized at module scope, so it
    // survives across tests in this file — clear both stores directly (via
    // an independent connection to the same database) for real isolation.
    const db = await openDB(dbNameFor('test-account'), DB_VERSION, {
      upgrade(db) {
        for (const name of STORES) {
          if (!db.objectStoreNames.contains(name)) db.createObjectStore(name, { keyPath: 'key' })
        }
      },
    })
    for (const name of STORES) await db.clear(name)
    db.close()
  })

  it('returns undefined for a missing key', async () => {
    expect(await getValue('playlist_order', 'missing')).toBeUndefined()
  })

  it('round-trips a value through set/get', async () => {
    await setValue('playlist_order', 'ids', ['a', 'b', 'c'])
    expect(await getValue('playlist_order', 'ids')).toEqual(['a', 'b', 'c'])
  })

  it('overwrites on repeated set', async () => {
    await setValue('playlist_order', 'ids', ['a'])
    await setValue('playlist_order', 'ids', ['b'])
    expect(await getValue('playlist_order', 'ids')).toEqual(['b'])
  })

  it('lists all stored values', async () => {
    await setValue('playlist_order', 'k1', 1)
    await setValue('playlist_order', 'k2', 2)
    expect(await listValues('playlist_order')).toEqual(expect.arrayContaining([1, 2]))
  })

  it('deletes a key', async () => {
    await setValue('playlist_order', 'to-delete', 'x')
    await deleteValue('playlist_order', 'to-delete')
    expect(await getValue('playlist_order', 'to-delete')).toBeUndefined()
  })

  it('accepts a Vue reactive Proxy without throwing (regression: DataCloneError)', async () => {
    const value = reactive({ ids: ['a', 'b'] })
    await expect(setValue('playlist_order', 'reactive', value)).resolves.toBeUndefined()
    expect(await getValue('playlist_order', 'reactive')).toEqual({ ids: ['a', 'b'] })
  })

  it('clearStore() removes every value in the store', async () => {
    await setValue('playlist_order', 'k1', 1)
    await setValue('playlist_order', 'k2', 2)
    await clearStore('playlist_order')
    expect(await listValues('playlist_order')).toEqual([])
  })
})
