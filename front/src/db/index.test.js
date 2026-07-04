import 'fake-indexeddb/auto'
import { describe, it, expect } from 'vitest'
import { reactive } from 'vue'
import { getValue, setValue, listValues, deleteValue } from './index'

describe('db (IndexedDB wrapper)', () => {
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
})
