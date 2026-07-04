import { openDB } from 'idb'

// Shared IndexedDB access for all local-persistence features (playlist
// order, watched state, history...). One object store per feature, all
// going through the same {key, value, updated_at} record shape so any of
// them could later be mirrored to a backend endpoint as-is, and so a
// future sync layer can do last-write-wins without a schema change.
const DB_NAME = 'ouyouyoutube'
const DB_VERSION = 2
const STORES = ['playlist_order', 'history']

let dbPromise

function getDb() {
  if (!dbPromise) {
    dbPromise = openDB(DB_NAME, DB_VERSION, {
      upgrade(db) {
        for (const name of STORES) {
          if (!db.objectStoreNames.contains(name)) {
            db.createObjectStore(name, { keyPath: 'key' })
          }
        }
      },
    })
  }
  return dbPromise
}

export async function getValue(store, key) {
  const db = await getDb()
  const record = await db.get(store, key)
  return record?.value
}

export async function setValue(store, key, value) {
  const db = await getDb()
  // JSON round-trip: strips Vue's reactive Proxy wrapping (which
  // IndexedDB's structured-clone algorithm can choke on if a caller
  // passes Pinia state straight through) and enforces the "plain
  // JSON-serializable value" contract these records are meant to keep.
  const plain = JSON.parse(JSON.stringify(value))
  await db.put(store, { key, value: plain, updated_at: new Date().toISOString() })
}

export async function listValues(store) {
  const db = await getDb()
  const records = await db.getAll(store)
  return records.map((r) => r.value)
}

export async function deleteValue(store, key) {
  const db = await getDb()
  await db.delete(store, key)
}
