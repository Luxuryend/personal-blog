<template>
  <!-- 应用根组件：仅提供路由视图和全局通知 -->
  <router-view />
</template>

<script setup>
/**
 * App.vue —— 应用根组件
 * onMounted 时尝试从 localStorage 恢复登录状态
 */
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

onMounted(() => {
  const authStore = useAuthStore()
  authStore.restoreSession()
})
</script>
