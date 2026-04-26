<template>
  <!-- 主布局：顶部导航 + 主体内容 + 底部版权 -->
  <div class="min-h-screen flex flex-col">
    <!-- 顶部导航 -->
    <nav class="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
      <div class="max-w-6xl mx-auto px-4">
        <div class="flex items-center justify-between h-16">
          <!-- Logo -->
          <router-link to="/" class="text-xl font-bold text-primary-600 hover:text-primary-700 transition-colors">
            MySite
          </router-link>

          <!-- 桌面端导航链接 -->
          <div class="hidden md:flex items-center space-x-6">
            <router-link to="/" class="text-gray-600 hover:text-primary-600 transition-colors">首页</router-link>
            <router-link to="/blog" class="text-gray-600 hover:text-primary-600 transition-colors">博客</router-link>
            <router-link to="/share" class="text-gray-600 hover:text-primary-600 transition-colors">分享</router-link>
            <router-link to="/guestbook" class="text-gray-600 hover:text-primary-600 transition-colors">留言板</router-link>
            <template v-if="authStore.isLoggedIn">
              <router-link v-if="authStore.isAdmin" to="/admin" class="text-gray-600 hover:text-primary-600 transition-colors font-medium">管理后台</router-link>
              <router-link to="/blog/editor" class="text-gray-600 hover:text-primary-600 transition-colors">写文章</router-link>
              <router-link to="/share/upload" class="text-gray-600 hover:text-primary-600 transition-colors">上传</router-link>
              <router-link to="/profile" class="text-gray-600 hover:text-primary-600 transition-colors text-sm">账户</router-link>
              <button @click="handleLogout" class="text-gray-500 hover:text-red-500 transition-colors text-sm">退出</button>
            </template>
            <template v-else>
              <router-link to="/login" class="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors text-sm">登录</router-link>
            </template>
          </div>

          <!-- 移动端菜单按钮 -->
          <button class="md:hidden p-2 text-gray-600" @click="mobileMenuOpen = !mobileMenuOpen">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="mobileMenuOpen ? 'M6 18L18 6M6 6l12 12' : 'M4 6h16M4 12h16M4 18h16'" />
            </svg>
          </button>
        </div>
      </div>

      <!-- 移动端下拉菜单 -->
      <div v-if="mobileMenuOpen" class="md:hidden border-t border-gray-100 bg-white">
        <div class="px-4 py-3 space-y-2">
          <router-link to="/" class="block py-2 text-gray-600" @click="mobileMenuOpen = false">首页</router-link>
          <router-link to="/blog" class="block py-2 text-gray-600" @click="mobileMenuOpen = false">博客</router-link>
          <router-link to="/share" class="block py-2 text-gray-600" @click="mobileMenuOpen = false">分享</router-link>
          <router-link to="/guestbook" class="block py-2 text-gray-600" @click="mobileMenuOpen = false">留言板</router-link>
          <template v-if="authStore.isLoggedIn">
            <router-link v-if="authStore.isAdmin" to="/admin" class="block py-2 text-primary-600 font-medium" @click="mobileMenuOpen = false">管理后台</router-link>
            <router-link to="/blog/editor" class="block py-2 text-gray-600" @click="mobileMenuOpen = false">写文章</router-link>
            <router-link to="/share/upload" class="block py-2 text-gray-600" @click="mobileMenuOpen = false">上传</router-link>
            <router-link to="/profile" class="block py-2 text-gray-600" @click="mobileMenuOpen = false">账户</router-link>
            <button @click="handleLogout" class="block py-2 text-red-500 w-full text-left">退出</button>
          </template>
        </div>
      </div>
    </nav>

    <!-- 主体内容 -->
    <main class="flex-1 max-w-6xl mx-auto w-full px-4 py-8">
      <!-- 通知 -->
      <div v-if="appStore.notification.show"
           class="mb-4 px-4 py-3 rounded-lg text-sm transition-all duration-300"
           :class="notificationClasses">
        {{ appStore.notification.message }}
      </div>

      <slot />
    </main>

    <!-- 底部 -->
    <footer class="bg-white border-t border-gray-200 py-6 text-center text-sm text-gray-500">
      <p>&copy; {{ new Date().getFullYear() }} MySite. Built with FastAPI &amp; Vue 3.</p>
    </footer>
  </div>
</template>

<script setup>
/**
 * MainLayout.vue —— 全局布局组件
 * 提供统一的导航栏、页脚和通知区域
 */
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'

const router = useRouter()
const authStore = useAuthStore()
const appStore = useAppStore()

const mobileMenuOpen = ref(false)

const notificationClasses = computed(() => ({
  'bg-green-50 text-green-700 border border-green-200': appStore.notification.type === 'success',
  'bg-red-50 text-red-700 border border-red-200': appStore.notification.type === 'error',
  'bg-blue-50 text-blue-700 border border-blue-200': appStore.notification.type === 'info',
}))

function handleLogout() {
  authStore.logout()
  router.push('/')
}
</script>
