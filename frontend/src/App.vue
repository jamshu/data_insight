<template>
  <div :class="{ 'dark': isDarkMode }" class="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
    <!-- Navigation Header -->
    <nav class="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <!-- Logo and Navigation -->
          <div class="flex items-center space-x-8">
            <router-link to="/" class="flex items-center space-x-3">
              <div class="w-10 h-10 rounded-lg gradient-bg flex items-center justify-center">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <span class="text-xl font-semibold text-gray-900 dark:text-white">Data Insights</span>
            </router-link>
            
            <div class="hidden sm:flex space-x-4">
              <router-link to="/" 
                          :class="[$route.name === 'Dashboard' ? 'text-primary-600 dark:text-primary-400' : 'text-gray-600 dark:text-gray-300']"
                          class="px-3 py-2 text-sm font-medium hover:text-primary-600 dark:hover:text-primary-400 transition-colors">
                Dashboard
              </router-link>
              <router-link to="/analysis" 
                          :class="[$route.name === 'Analysis' ? 'text-primary-600 dark:text-primary-400' : 'text-gray-600 dark:text-gray-300']"
                          class="px-3 py-2 text-sm font-medium hover:text-primary-600 dark:hover:text-primary-400 transition-colors">
                Analysis
              </router-link>
              <router-link to="/settings" 
                          :class="[$route.name === 'Settings' ? 'text-primary-600 dark:text-primary-400' : 'text-gray-600 dark:text-gray-300']"
                          class="px-3 py-2 text-sm font-medium hover:text-primary-600 dark:hover:text-primary-400 transition-colors">
                Settings
              </router-link>
            </div>
          </div>
          
          <!-- Right side actions -->
          <div class="flex items-center space-x-4">
            <!-- Dark mode toggle -->
            <button @click="toggleDarkMode" 
                    class="p-2 rounded-lg text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
              <svg v-if="!isDarkMode" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            </button>
            
            <!-- Upload button -->
            <button @click="showUploadModal = true" class="btn-primary flex items-center space-x-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <span>Upload Data</span>
            </button>
          </div>
        </div>
      </div>
    </nav>
    
    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    
    <!-- Upload Modal -->
    <FileUploadModal v-if="showUploadModal" @close="showUploadModal = false" @uploaded="handleFileUploaded" />
    
    <!-- Notification Toast -->
    <NotificationToast />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import FileUploadModal from './components/FileUploadModal.vue'
import NotificationToast from './components/NotificationToast.vue'

const router = useRouter()
const isDarkMode = ref(false)
const showUploadModal = ref(false)

// Load dark mode preference
onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    isDarkMode.value = true
    document.documentElement.classList.add('dark')
  }
})

// Toggle dark mode
const toggleDarkMode = () => {
  isDarkMode.value = !isDarkMode.value
  if (isDarkMode.value) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  }
}

// Handle file uploaded
const handleFileUploaded = (sessionId) => {
  showUploadModal.value = false
  router.push(`/analysis/${sessionId}`)
}
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
