import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import PlaylistDetail from '../views/PlaylistDetail.vue'
import Player from '../views/Player.vue'

const routes = [
  { path: '/', name: 'home', component: Home },
  { path: '/playlist/:id', name: 'playlist', component: PlaylistDetail, props: true },
  { path: '/watch/:videoId', name: 'player', component: Player, props: true },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})
