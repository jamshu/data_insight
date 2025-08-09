<template>
  <transition-group name="notification" tag="div" class="fixed top-4 right-4 z-50 space-y-2">
    <div
      v-for="notification in notifications"
      :key="notification.id"
      :class="[
        'max-w-sm px-4 py-3 rounded-lg shadow-lg flex items-center space-x-3 animate-slide-up',
        notification.type === 'success' ? 'bg-green-500 text-white' : '',
        notification.type === 'error' ? 'bg-red-500 text-white' : '',
        notification.type === 'warning' ? 'bg-yellow-500 text-white' : '',
        notification.type === 'info' ? 'bg-blue-500 text-white' : ''
      ]"
    >
      <svg v-if="notification.type === 'success'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
      </svg>
      <svg v-else-if="notification.type === 'error'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
      <svg v-else-if="notification.type === 'warning'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
      <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <span class="text-sm font-medium">{{ notification.message }}</span>
    </div>
  </transition-group>
</template>

<script setup>
import { onMounted } from 'vue'
import { notifications, removeNotification } from '../utils/notification'

onMounted(() => {
  // Auto remove notifications after 3 seconds
  setInterval(() => {
    const now = Date.now()
    notifications.value = notifications.value.filter(n => now - n.timestamp < 3000)
  }, 100)
})
</script>

<style scoped>
.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.notification-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

.notification-move {
  transition: transform 0.3s ease;
}
</style>
