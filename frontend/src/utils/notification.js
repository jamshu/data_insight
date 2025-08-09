import { ref } from 'vue'

export const notifications = ref([])

let notificationId = 0

export const showNotification = (message, type = 'info') => {
  const notification = {
    id: notificationId++,
    message,
    type,
    timestamp: Date.now()
  }
  notifications.value.push(notification)
}

export const removeNotification = (id) => {
  const index = notifications.value.findIndex(n => n.id === id)
  if (index > -1) {
    notifications.value.splice(index, 1)
  }
}

export const useNotification = () => {
  return {
    notifications,
    showNotification,
    removeNotification
  }
}
