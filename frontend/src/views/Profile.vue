<template>
  <MainLayout>
    <div class="max-w-2xl mx-auto">
      <h1 class="text-3xl font-bold mb-8">个人设置</h1>

      <!-- 当前信息 -->
      <div class="bg-white rounded-xl border border-gray-100 p-6 mb-6">
        <h2 class="text-lg font-semibold mb-4">账户信息</h2>
        <div class="space-y-2 text-sm">
          <div class="flex items-center gap-2">
            <span class="text-gray-500 w-20">用户名：</span>
            <span class="text-gray-900">{{ authStore.user?.username }}</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-gray-500 w-20">角色：</span>
            <span class="text-gray-900">{{ authStore.user?.role === 'admin' ? '管理员' : '访客' }}</span>
          </div>
        </div>
      </div>

      <!-- 修改表单 -->
      <div class="bg-white rounded-xl border border-gray-100 p-6">
        <h2 class="text-lg font-semibold mb-4">修改资料</h2>
        <form @submit.prevent="handleUpdate" class="space-y-4">
          <div>
            <label class="block text-sm text-gray-600 mb-1">昵称</label>
            <input v-model="form.nickname" type="text" maxlength="50" placeholder="输入新昵称"
              class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none" />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">新密码</label>
            <input v-model="form.password" type="password" minlength="6" maxlength="100" placeholder="留空则不修改密码"
              class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
              :disabled="authStore.user?.role === 'admin'" />
            <p v-if="authStore.user?.role === 'admin'" class="text-xs text-gray-400 mt-1">
              管理员密码请直接修改 .env 配置文件中的 ADMIN_PASSWORD
            </p>
          </div>
          <button type="submit" :disabled="submitting"
            class="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors">
            {{ submitting ? '保存中...' : '保存修改' }}
          </button>
        </form>
      </div>
    </div>
  </MainLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import MainLayout from '@/layouts/MainLayout.vue'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'
import { authApi } from '@/api/auth'

const authStore = useAuthStore()
const appStore = useAppStore()

const submitting = ref(false)
const form = ref({ nickname: '', password: '' })

onMounted(() => {
  if (authStore.user?.nickname) {
    form.value.nickname = authStore.user.nickname
  }
})

async function handleUpdate() {
  submitting.value = true
  try {
    const data = {}
    if (form.value.nickname) data.nickname = form.value.nickname
    if (form.value.password) data.password = form.value.password
    if (!Object.keys(data).length) return

    await authApi.updateMe(data)
    // 刷新用户信息
    await authStore.restoreSession()
    appStore.showNotification('个人信息已更新', 'success')
  } catch (e) {
    appStore.showNotification(e.message || '更新失败', 'error')
  } finally {
    submitting.value = false
  }
}
</script>
