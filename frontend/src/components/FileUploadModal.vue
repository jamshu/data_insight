<template>
  <div class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
      <!-- Background overlay -->
      <div @click="$emit('close')" class="fixed inset-0 transition-opacity bg-gray-500 dark:bg-gray-900 bg-opacity-75 dark:bg-opacity-75"></div>

      <!-- Modal panel -->
      <div class="inline-block w-full max-w-2xl px-4 pt-5 pb-4 overflow-hidden text-left align-bottom transition-all transform bg-white dark:bg-gray-800 rounded-lg shadow-xl sm:my-8 sm:align-middle sm:p-6">
        <div class="absolute top-0 right-0 pt-4 pr-4">
          <button @click="$emit('close')" class="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300">
            <span class="sr-only">Close</span>
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="sm:flex sm:items-start">
          <div class="w-full mt-3 text-center sm:mt-0 sm:text-left">
            <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-white">
              Upload Data File
            </h3>
            <div class="mt-2">
              <p class="text-sm text-gray-500 dark:text-gray-400">
                Upload CSV or Excel files to analyze. Maximum file size: 100MB
              </p>
            </div>

            <!-- Drop zone -->
            <div
              @drop="handleDrop"
              @dragover.prevent
              @dragenter.prevent
              @dragleave="isDragging = false"
              :class="[
                'mt-4 border-2 border-dashed rounded-lg p-8 text-center transition-colors',
                isDragging ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20' : 'border-gray-300 dark:border-gray-600',
                uploadProgress > 0 ? 'pointer-events-none' : ''
              ]"
            >
              <input
                ref="fileInput"
                type="file"
                accept=".csv,.xlsx,.xls"
                @change="handleFileSelect"
                class="hidden"
                :disabled="uploadProgress > 0"
              />

              <div v-if="uploadProgress === 0">
                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
                  <button @click="$refs.fileInput.click()" class="font-medium text-primary-600 hover:text-primary-500">
                    Click to upload
                  </button>
                  or drag and drop
                </p>
                <p class="text-xs text-gray-500 dark:text-gray-400">CSV, XLSX up to 100MB</p>
              </div>

              <!-- Upload progress -->
              <div v-else class="space-y-4">
                <div class="flex items-center justify-center space-x-2">
                  <svg class="animate-spin h-8 w-8 text-primary-600" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Uploading...</span>
                </div>
                <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div class="bg-primary-600 h-2 rounded-full transition-all duration-300" :style="`width: ${uploadProgress}%`"></div>
                </div>
                <p class="text-sm text-gray-500 dark:text-gray-400">{{ uploadProgress }}% complete</p>
              </div>
            </div>

            <!-- Selected file info -->
            <div v-if="selectedFile && uploadProgress === 0" class="mt-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-3">
                  <svg class="h-8 w-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <div>
                    <p class="text-sm font-medium text-gray-900 dark:text-white">{{ selectedFile.name }}</p>
                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ formatFileSize(selectedFile.size) }}</p>
                  </div>
                </div>
                <button @click="clearFile" class="text-red-500 hover:text-red-700">
                  <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Error message -->
            <div v-if="errorMessage" class="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <p class="text-sm text-red-600 dark:text-red-400">{{ errorMessage }}</p>
            </div>

            <!-- Actions -->
            <div class="mt-6 flex justify-end space-x-3">
              <button @click="$emit('close')" class="btn-secondary" :disabled="uploadProgress > 0">
                Cancel
              </button>
              <button @click="uploadFile" class="btn-primary" :disabled="!selectedFile || uploadProgress > 0">
                Upload & Analyze
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useNotification } from '../utils/notification'

const emit = defineEmits(['close', 'uploaded'])
const { showNotification } = useNotification()

const fileInput = ref(null)
const selectedFile = ref(null)
const isDragging = ref(false)
const uploadProgress = ref(0)
const errorMessage = ref('')

const handleDrop = (e) => {
  e.preventDefault()
  isDragging.value = false
  
  const files = e.dataTransfer.files
  if (files.length > 0) {
    selectFile(files[0])
  }
}

const handleFileSelect = (e) => {
  const files = e.target.files
  if (files.length > 0) {
    selectFile(files[0])
  }
}

const selectFile = (file) => {
  errorMessage.value = ''
  
  // Validate file type
  const validTypes = ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
  if (!validTypes.includes(file.type) && !file.name.match(/\.(csv|xlsx|xls)$/i)) {
    errorMessage.value = 'Please select a CSV or Excel file'
    return
  }
  
  // Validate file size (100MB)
  if (file.size > 100 * 1024 * 1024) {
    errorMessage.value = 'File size must be less than 100MB'
    return
  }
  
  selectedFile.value = file
}

const clearFile = () => {
  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const uploadFile = async () => {
  if (!selectedFile.value) return
  
  const formData = new FormData()
  formData.append('file', selectedFile.value)
  
  try {
    uploadProgress.value = 1
    
    const response = await axios.post('/api/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        uploadProgress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total)
      }
    })
    
    showNotification('File uploaded successfully!', 'success')
    emit('uploaded', response.data.session_id)
  } catch (error) {
    console.error('Upload error:', error)
    errorMessage.value = error.response?.data?.detail || 'Failed to upload file'
    uploadProgress.value = 0
    showNotification('Failed to upload file', 'error')
  }
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}
</script>
