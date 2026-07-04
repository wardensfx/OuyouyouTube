import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import PlaylistDetail from '../views/PlaylistDetail.vue'
import Player from '../views/Player.vue'
import Search from '../views/Search.vue'
import ManagePlaylists from '../views/ManagePlaylists.vue'
import Liked from '../views/Liked.vue'
import Subscriptions from '../views/Subscriptions.vue'
import Trending from '../views/Trending.vue'

const routes = [
  { path: '/', name: 'home', component: Home },
  { path: '/playlist/:id', name: 'playlist', component: PlaylistDetail, props: true },
  { path: '/playlists/manage', name: 'manage-playlists', component: ManagePlaylists },
  { path: '/favorites', name: 'favorites', component: Liked },
  { path: '/subscriptions', name: 'subscriptions', component: Subscriptions },
  { path: '/trending', name: 'trending', component: Trending },
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
