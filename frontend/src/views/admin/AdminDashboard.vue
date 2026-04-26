<template>
  <MainLayout>
    <div class="max-w-5xl mx-auto">
      <h1 class="text-3xl font-bold mb-8">管理后台</h1>

      <!-- 统计卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div class="bg-white rounded-xl border border-gray-100 p-5">
          <div class="text-2xl font-bold text-primary-600">{{ stats.pendingMessages }}</div>
          <div class="text-sm text-gray-500 mt-1">待审核留言</div>
        </div>
        <div class="bg-white rounded-xl border border-gray-100 p-5">
          <div class="text-2xl font-bold text-green-600">{{ stats.publishedPosts }}</div>
          <div class="text-sm text-gray-500 mt-1">已发布文章</div>
        </div>
        <div class="bg-white rounded-xl border border-gray-100 p-5">
          <div class="text-2xl font-bold text-amber-600">{{ stats.totalShares }}</div>
          <div class="text-sm text-gray-500 mt-1">分享文件</div>
        </div>
        <div class="bg-white rounded-xl border border-gray-100 p-5">
          <div class="text-2xl font-bold text-purple-600">{{ stats.totalMessages }}</div>
          <div class="text-sm text-gray-500 mt-1">总留言数</div>
        </div>
      </div>

      <!-- 留言审核面板 -->
      <div class="bg-white rounded-xl border border-gray-100 p-6 mb-8">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-semibold">留言审核</h2>
          <span v-if="pendingMessages.length" class="bg-red-100 text-red-600 text-xs px-2 py-1 rounded-full">
            {{ pendingMessages.length }} 条待审核
          </span>
        </div>

        <div v-if="loadingPending" class="text-center py-6 text-gray-400">加载中...</div>

        <div v-else-if="pendingMessages.length === 0" class="text-center py-6 text-gray-400 text-sm">
          暂无待审核的留言
        </div>

        <div v-else class="space-y-4">
          <div v-for="msg in pendingMessages" :key="msg.id"
            class="border border-gray-100 rounded-lg p-4 hover:border-amber-200 transition-colors">
            <div class="flex items-start justify-between mb-2">
              <div>
                <span class="font-medium text-gray-900">{{ msg.nickname }}</span>
                <span class="text-xs text-gray-400 ml-2">{{ new Date(msg.created_at).toLocaleString('zh-CN') }}</span>
              </div>
              <div v-if="msg.ip_address" class="text-xs text-gray-400">{{ msg.ip_address }}</div>
            </div>
            <p class="text-gray-700 mb-3 whitespace-pre-wrap">{{ msg.content }}</p>
            <div class="flex gap-2">
              <button @click="handleApprove(msg.id, true)"
                class="px-4 py-1.5 bg-green-500 text-white text-sm rounded-lg hover:bg-green-600 transition-colors">
                通过
              </button>
              <button @click="handleApprove(msg.id, false)"
                class="px-4 py-1.5 bg-red-500 text-white text-sm rounded-lg hover:bg-red-600 transition-colors">
                拒绝
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 快捷入口 -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <router-link to="/admin/blogs"
          class="block bg-white rounded-xl border border-gray-100 p-5 hover:shadow-sm transition-shadow">
          <h3 class="font-semibold mb-1">📝 博客管理</h3>
          <p class="text-sm text-gray-500">查看、编辑、删除所有文章</p>
        </router-link>
        <router-link to="/admin/shares"
          class="block bg-white rounded-xl border border-gray-100 p-5 hover:shadow-sm transition-shadow">
          <h3 class="font-semibold mb-1">📁 分享管理</h3>
          <p class="text-sm text-gray-500">管理所有分享文件，开关/删除</p>
        </router-link>
        <router-link to="/share/upload"
          class="block bg-white rounded-xl border border-gray-100 p-5 hover:shadow-sm transition-shadow">
          <h3 class="font-semibold mb-1">📤 上传文件</h3>
          <p class="text-sm text-gray-500">分享新的文件或图片</p>
        </router-link>
      </div>
    </div>
  </MainLayout>
</template>

<script setup>
/**
 * AdminDashboard.vue —— 管理后台
 * 留言审核、统计概览、快捷入口
 */
import { ref, onMounted } from 'vue'
import MainLayout from '@/layouts/MainLayout.vue'
import { guestbookApi } from '@/api/guestbook'
import { blogApi } from '@/api/blog'
import { shareApi } from '@/api/share'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()

const stats = ref({
  pendingMessages: 0,
  publishedPosts: 0,
  totalShares: 0,
  totalMessages: 0,
})

const pendingMessages = ref([])
const loadingPending = ref(true)

async function fetchPendingMessages() {
  loadingPending.value = true
  try {
    const data = await guestbookApi.listAllMessagesAdmin({ page: 1, page_size: 50 })
    const all = data.items || []
    // 筛选未审核的一级留言
    pendingMessages.value = all.filter(m => !m.is_approved && !m.parent_id)
    stats.value.pendingMessages = pendingMessages.value.length
    stats.value.totalMessages = data.pagination?.total || 0
  } catch {
    pendingMessages.value = []
  } finally {
    loadingPending.value = false
  }
}

async function handleApprove(id, approved) {
  try {
    await guestbookApi.reviewMessage(id, { is_approved: approved })
    pendingMessages.value = pendingMessages.value.filter(m => m.id !== id)
    stats.value.pendingMessages = pendingMessages.value.length
    appStore.showNotification(approved ? '留言已通过审核' : '留言已拒绝', 'success')
  } catch (e) {
    appStore.showNotification(e.message || '操作失败', 'error')
  }
}

async function fetchStats() {
  try {
    const blogData = await blogApi.listPosts({ page: 1, page_size: 1 })
    stats.value.publishedPosts = blogData.pagination?.total || 0
  } catch { /* ignore */ }

  try {
    const shareData = await shareApi.listShares({ page: 1, page_size: 1 })
    stats.value.totalShares = shareData.pagination?.total || 0
  } catch { /* ignore */ }
}

onMounted(() => {
  fetchPendingMessages()
  fetchStats()
})
</script>
