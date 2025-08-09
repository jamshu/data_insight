import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './assets/main.css'

// Import views
import Dashboard from './views/Dashboard.vue'
import Analysis from './views/Analysis.vue'
import Settings from './views/Settings.vue'

// Define routes
const routes = [
  { path: '/', name: 'Dashboard', component: Dashboard },
  { path: '/analysis/:sessionId?', name: 'Analysis', component: Analysis },
  { path: '/settings', name: 'Settings', component: Settings }
]

// Create router
const router = createRouter({
  history: createWebHistory(),
  routes
})

// Create and mount app
const app = createApp(App)
app.use(router)
app.mount('#app')
