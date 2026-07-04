import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import PlaylistDetail from '../views/PlaylistDetail.vue'
import Player from '../views/Player.vue'
import Search from '../views/Search.vue'

const routes = [
  { path: '/', name: 'home', component: Home },
  { path: '/playlist/:id', name: 'playlist', component: PlaylistDetail, props: true },
  { path: '/watch/:videoId', name: 'player', component: Player, props: true },
  { path: '/search', name: 'search', component: Search, props: (route) => ({ q: route.query.q || '' }) },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // Restaure la position de scroll au retour (navigation arrière), sinon
    // repart du haut sur une nouvelle navigation.
    return savedPosition || { top: 0 }
  },
})
