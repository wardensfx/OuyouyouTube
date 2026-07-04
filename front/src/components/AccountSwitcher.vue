<script setup>
import { ref, onMounted, computed } from 'vue'
import { UserPlus, LogOut } from '@lucide/vue'
import { api } from '../api/client'

const accounts = ref([])
const open = ref(false)

async function load() {
  accounts.value = (await api.getAccounts()) || []
}

const active = computed(() => accounts.value.find((a) => a.active))

function initials(account) {
  const source = account?.name || account?.email || '?'
  return source.trim().charAt(0).toUpperCase()
}

function avatarStyle(account) {
  // Proxifié + caché côté backend (2h) : évite de re-taper le CDN Google à
  // chaque reload, qui finissait par nous 429.
  return account?.picture ? { backgroundImage: `url(/auth/accounts/${account.id}/avatar)` } : {}
}

async function activate(id) {
  open.value = false
  if (id === active.value?.id) return
  await api.activateAccount(id)
  window.location.reload()
}

function addAccount() {
  window.location.href = api.loginUrl({ link: true })
}

async function logout() {
  await api.logout()
  window.location.href = '/'
}

onMounted(load)
</script>

<template>
  <div class="switcher">
    <button class="switcher__trigger" @click="open = !open">
      <span class="avatar" :style="avatarStyle(active)">
        <span v-if="!active?.picture">{{ initials(active) }}</span>
      </span>
      <span class="switcher__name">{{ active?.name || active?.email || '…' }}</span>
    </button>

    <div v-if="open" class="switcher__backdrop" @click="open = false" />
    <Transition name="pop">
      <div v-if="open" class="switcher__panel glass glass--strong">
        <button
          v-for="a in accounts"
          :key="a.id"
          class="switcher__row"
          :class="{ 'switcher__row--active': a.active }"
          @click="activate(a.id)"
        >
          <span class="avatar avatar--sm" :style="avatarStyle(a)">
            <span v-if="!a.picture">{{ initials(a) }}</span>
          </span>
          <span class="switcher__row-text">
            <span class="switcher__row-name">{{ a.name || a.email }}</span>
            <span class="switcher__row-email">{{ a.email }}</span>
          </span>
        </button>

        <div class="switcher__divider" />
        <button class="switcher__action" @click="addAccount">
          <UserPlus :size="16" /> Ajouter un compte
        </button>
        <button class="switcher__action switcher__action--danger" @click="logout">
          <LogOut :size="16" /> Se déconnecter
        </button>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.switcher {
  position: relative;
}
.switcher__trigger {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: transparent;
  border: none;
  color: inherit;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 999px;
}
.switcher__trigger:hover {
  background: rgba(255, 255, 255, 0.08);
}
.switcher__name {
  font-size: 0.85rem;
  max-width: 10rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background-color: #333;
  background-position: center;
  background-size: cover;
  background-repeat: no-repeat;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 600;
  flex-shrink: 0;
}
.avatar--sm {
  width: 32px;
  height: 32px;
}
.switcher__backdrop {
  position: fixed;
  inset: 0;
  z-index: 20;
}
.switcher__panel {
  position: absolute;
  right: 0;
  top: calc(100% + 0.5rem);
  border-radius: var(--radius-lg);
  min-width: 220px;
  padding: 0.4rem;
  z-index: 21;
  transform-origin: top right;
}
.pop-enter-active,
.pop-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.pop-enter-from,
.pop-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(-4px);
}
.switcher__row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  width: 100%;
  background: transparent;
  border: none;
  color: inherit;
  text-align: left;
  padding: 0.5rem;
  border-radius: 8px;
  cursor: pointer;
}
.switcher__row:hover {
  background: rgba(255, 255, 255, 0.1);
}
.switcher__row--active {
  background: rgba(255, 255, 255, 0.1);
}
.switcher__row-text {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.switcher__row-name {
  font-size: 0.85rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.switcher__row-email {
  font-size: 0.72rem;
  opacity: 0.6;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.switcher__divider {
  height: 1px;
  background: var(--glass-border);
  margin: 0.3rem 0;
}
.switcher__action {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  background: transparent;
  border: none;
  color: inherit;
  text-align: left;
  padding: 0.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
}
.switcher__action:hover {
  background: rgba(255, 255, 255, 0.1);
}
.switcher__action--danger {
  color: var(--danger);
}
</style>
