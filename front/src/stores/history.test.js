import 'fake-indexeddb/auto'
import { openDB } from 'idb'
import { describe, it, expect, beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useHistoryStore } from './history'

const video = (id, title = `Title ${id}`) => ({
  video_id: id,
  title,
  channel: 'Channel',
  channel_id: 'UC123',
  thumbnail: 'https://example.com/thumb.jpg',
  duration: 'PT5M',
})

describe('useHistoryStore', () => {
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
    await db.clear('history')
    db.close()
  })

  it('starts empty', async () => {
    const store = useHistoryStore()
    await store.load()
    expect(store.entries).toEqual([])
  })

  it('records a video at the front of the list with a watched_at timestamp', async () => {
    const store = useHistoryStore()
    await store.record(video('v1'))
    expect(store.entries).toHaveLength(1)
    expect(store.entries[0]).toMatchObject({ video_id: 'v1', title: 'Title v1' })
    expect(typeof store.entries[0].watched_at).toBe('string')
  })

  it('moves a re-watched video back to the front instead of duplicating it', async () => {
    const store = useHistoryStore()
    await store.record(video('v1'))
    await store.record(video('v2'))
    await store.record(video('v1'))
    expect(store.entries.map((e) => e.video_id)).toEqual(['v1', 'v2'])
  })

  it('caps the history at 200 entries, dropping the oldest', async () => {
    const store = useHistoryStore()
    for (let i = 0; i < 205; i++) {
      await store.record(video(`v${i}`))
    }
    expect(store.entries).toHaveLength(200)
    expect(store.entries[0].video_id).toBe('v204')
    expect(store.entries.map((e) => e.video_id)).not.toContain('v0')
  })

  it('persists across a simulated reload', async () => {
    const store = useHistoryStore()
    await store.record(video('v1'))

    setActivePinia(createPinia())
    const reloaded = useHistoryStore()
    await reloaded.load()
    expect(reloaded.entries.map((e) => e.video_id)).toEqual(['v1'])
  })
})
