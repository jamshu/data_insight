<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Settings</h1>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        Configure your data analysis platform preferences
      </p>
    </div>

    <!-- Settings Sections -->
    <div class="space-y-6">
      <!-- General Settings -->
      <div class="card">
        <div class="p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">General Settings</h2>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Default Export Format
            </label>
            <select v-model="settings.exportFormat" class="input-field">
              <option value="csv">CSV</option>
              <option value="excel">Excel</option>
              <option value="json">JSON</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Max File Size (MB)
            </label>
            <input v-model.number="settings.maxFileSize" type="number" class="input-field" min="1" max="500">
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Auto-refresh Interval (seconds)
            </label>
            <input v-model.number="settings.refreshInterval" type="number" class="input-field" min="5" max="300">
          </div>
        </div>
      </div>

      <!-- Analysis Settings -->
      <div class="card">
        <div class="p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Analysis Settings</h2>
        </div>
        <div class="p-6 space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-700 dark:text-gray-300">Detect Outliers</p>
              <p class="text-xs text-gray-500 dark:text-gray-400">Automatically detect outliers in numeric columns</p>
            </div>
            <button @click="settings.detectOutliers = !settings.detectOutliers" 
                    :class="[
                      'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                      settings.detectOutliers ? 'bg-primary-600' : 'bg-gray-200 dark:bg-gray-700'
                    ]">
              <span :class="[
                      'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                      settings.detectOutliers ? 'translate-x-6' : 'translate-x-1'
                    ]" />
            </button>
          </div>
          
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-700 dark:text-gray-300">Calculate Correlations</p>
              <p class="text-xs text-gray-500 dark:text-gray-400">Compute correlation matrix for numeric columns</p>
            </div>
            <button @click="settings.calculateCorrelations = !settings.calculateCorrelations" 
                    :class="[
                      'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                      settings.calculateCorrelations ? 'bg-primary-600' : 'bg-gray-200 dark:bg-gray-700'
                    ]">
              <span :class="[
                      'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                      settings.calculateCorrelations ? 'translate-x-6' : 'translate-x-1'
                    ]" />
            </button>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Sample Size (rows)
            </label>
            <input v-model.number="settings.sampleSize" type="number" class="input-field" min="10" max="1000">
          </div>
        </div>
      </div>

      <!-- Visualization Settings -->
      <div class="card">
        <div class="p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Visualization Settings</h2>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Chart Color Scheme
            </label>
            <select v-model="settings.colorScheme" class="input-field">
              <option value="default">Default</option>
              <option value="colorful">Colorful</option>
              <option value="monochrome">Monochrome</option>
              <option value="pastel">Pastel</option>
            </select>
          </div>
          
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-700 dark:text-gray-300">Show Grid Lines</p>
              <p class="text-xs text-gray-500 dark:text-gray-400">Display grid lines on charts</p>
            </div>
            <button @click="settings.showGridLines = !settings.showGridLines" 
                    :class="[
                      'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                      settings.showGridLines ? 'bg-primary-600' : 'bg-gray-200 dark:bg-gray-700'
                    ]">
              <span :class="[
                      'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                      settings.showGridLines ? 'translate-x-6' : 'translate-x-1'
                    ]" />
            </button>
          </div>
        </div>
      </div>

      <!-- Data Management -->
      <div class="card">
        <div class="p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Data Management</h2>
        </div>
        <div class="p-6 space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-700 dark:text-gray-300">Clear All Sessions</p>
              <p class="text-xs text-gray-500 dark:text-gray-400">Remove all uploaded files and analysis data</p>
            </div>
            <button @click="clearSessions" class="px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600">
              Clear Data
            </button>
          </div>
          
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-700 dark:text-gray-300">Cache Duration</p>
              <p class="text-xs text-gray-500 dark:text-gray-400">How long to keep analysis results cached</p>
            </div>
            <select v-model="settings.cacheDuration" class="input-field w-32">
              <option value="1">1 hour</option>
              <option value="6">6 hours</option>
              <option value="24">24 hours</option>
              <option value="168">1 week</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex justify-end space-x-3">
        <button @click="resetSettings" class="btn-secondary">
          Reset to Defaults
        </button>
        <button @click="saveSettings" class="btn-primary">
          Save Settings
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useNotification } from '../utils/notification'
import axios from 'axios'

const { showNotification } = useNotification()

const settings = ref({
  exportFormat: 'csv',
  maxFileSize: 100,
  refreshInterval: 30,
  detectOutliers: true,
  calculateCorrelations: true,
  sampleSize: 100,
  colorScheme: 'default',
  showGridLines: true,
  cacheDuration: 24
})

const defaultSettings = { ...settings.value }

const loadSettings = () => {
  const saved = localStorage.getItem('dataInsightsSettings')
  if (saved) {
    try {
      settings.value = JSON.parse(saved)
    } catch (e) {
      console.error('Failed to load settings:', e)
    }
  }
}

const saveSettings = () => {
  localStorage.setItem('dataInsightsSettings', JSON.stringify(settings.value))
  showNotification('Settings saved successfully', 'success')
}

const resetSettings = () => {
  settings.value = { ...defaultSettings }
  showNotification('Settings reset to defaults', 'info')
}

const clearSessions = async () => {
  if (confirm('Are you sure you want to clear all sessions? This action cannot be undone.')) {
    try {
      await axios.delete('/api/sessions/clear/')
      showNotification('All sessions cleared successfully', 'success')
    } catch (error) {
      console.error('Failed to clear sessions:', error)
      showNotification('Failed to clear sessions', 'error')
    }
  }
}

onMounted(() => {
  loadSettings()
})
</script>
