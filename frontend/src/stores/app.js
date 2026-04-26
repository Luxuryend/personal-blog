/**
 * 全局应用状态管理
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  /** 侧边栏是否展开（移动端） */
  const sidebarOpen = ref(false)

  /** 全局加载状态 */
  const globalLoading = ref(false)

  /** 通知消息 */
  const notification = ref({ show: false, message: '', type: 'info' })

  function toggleSidebar() {
    sidebarOpen.value = !sidebarOpen.value
  }

  function showNotification(message, type = 'info', duration = 3000) {
    notification.value = { show: true, message, type }
    setTimeout(() => {
      notification.value.show = false
    }, duration)
  }

  return {
    sidebarOpen,
    globalLoading,
    notification,
    toggleSidebar,
    showNotification,
  }
})
