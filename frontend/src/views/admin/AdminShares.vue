<template>
  <MainLayout>
    <div class="max-w-5xl mx-auto">
      <div class="flex items-center justify-between mb-6">
        <div>
          <h1 class="text-3xl font-bold">分享管理</h1>
          <p class="text-sm text-gray-500 mt-1">共 {{ pagination.total }} 个文件</p>
        </div>
        <router-link to="/share/upload"
          class="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors text-sm">
          + 上传文件
        </router-link>
      </div>

      <div v-if="loading" class="text-center py-12 text-gray-400">加载中...</div>

      <div v-else-if="shares.length === 0" class="text-center py-12 text-gray-400">暂无分享</div>

      <div v-else class="bg-white rounded-xl border border-gray-100 overflow-hidden">
        <table class="w-full">
          <thead class="bg-gray-50 border-b border-gray-100">
            <tr class="text-left text-sm text-gray-500">
              <th class="px-4 py-3 font-medium">文件名</th>
              <th class="px-4 py-3 font-medium hidden md:table-cell">类型</th>
              <th class="px-4 py-3 font-medium hidden sm:table-cell">大小</th>
              <th class="px-4 py-3 font-medium">状态</th>
              <th class="px-4 py-3 font-medium hidden lg:table-cell">下载</th>
              <th class="px-4 py-3 font-medium hidden lg:table-cell">时间</th>
              <th class="px-4 py-3 font-medium text-right">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="item in shares" :key="item.id" class="hover:bg-gray-50/50 transition-colors">
              <td class="px-4 py-3">
                <div class="flex items-center gap-2">
                  <span v-if="item.is_image" class="text-lg">🖼</span>
                  <span v-else class="text-lg">📄</span>
                  <router-link :to="`/share/${item.id}`" class="text-gray-900 hover:text-primary-600 truncate max-w-[200px] inline-block">
                    {{ item.original_name }}
                  </router-link>
                </div>
              </td>
              <td class="px-4 py-3 text-sm text-gray-500 hidden md:table-cell">{{ item.file_type || '-' }}</td>
              <td class="px-4 py-3 text-sm text-gray-500 hidden sm:table-cell">{{ formatSize(item.file_size) }}</td>
              <td class="px-4 py-3">
                <span v-if="!item.is_active" class="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full">已关闭</span>
                <span v-else-if="isExpired(item)" class="text-xs bg-red-100 text-red-500 px-2 py-0.5 rounded-full">已过期</span>
                <span v-else class="text-xs bg-green-100 text-green-600 px-2 py-0.5 rounded-full">有效</span>
              </td>
              <td class="px-4 py-3 text-sm text-gray-500 hidden lg:table-cell">
                {{ item.download_count }}{{ item.max_downloads ? `/${item.max_downloads}` : '' }}
              </td>
              <td class="px-4 py-3 text-sm text-gray-500 hidden lg:table-cell">
                {{ new Date(item.created_at).toLocaleDateString('zh-CN') }}
              </td>
              <td class="px-4 py-3 text-right">
                <div class="flex items-center justify-end gap-2">
                  <button @click="toggleActive(item)"
                    class="text-xs px-2 py-1 rounded"
                    :class="item.is_active ? 'text-amber-600 hover:text-amber-700' : 'text-green-600 hover:text-green-700'">
                    {{ item.is_active ? '关闭' : '启用' }}
                  </button>
                  <button @click="handleDelete(item)"
                    class="text-xs text-red-500 hover:text-red-600 px-2 py-1">
                    删除
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页 -->
      <div v-if="pagination.total_pages > 1" class="flex justify-center items-center gap-4 mt-6">
        <button :disabled="pagination.page <= 1" @click="changePage(pagination.page - 1)"
          class="px-4 py-2 text-sm bg-white border border-gray-200 rounded-lg disabled:opacity-50 hover:bg-gray-50">
          上一页
        </button>
        <span class="text-sm text-gray-500">{{ pagination.page }} / {{ pagination.total_pages }}</span>
        <button :disabled="pagination.page >= pagination.total_pages" @click="changePage(pagination.page + 1)"
          class="px-4 py-2 text-sm bg-white border border-gray-200 rounded-lg disabled:opacity-50 hover:bg-gray-50">
          下一页
        </button>
      </div>
    </div>
  </MainLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import MainLayout from '@/layouts/MainLayout.vue'
import { shareApi } from '@/api/share'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()
const shares = ref([])
const loading = ref(true)
const pagination = ref({ page: 1, page_size: 20, total: 0, total_pages: 0 })

function formatSize(bytes) {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  let size = bytes
  while (size >= 1024 && i < units.length - 1) { size /= 1024; i++ }
  return `${size.toFixed(1)} ${units[i]}`
}

function isExpired(item) {
  if (!item.expires_at) return false
  return new Date(item.expires_at) < new Date()
}

async function fetchShares() {
  loading.value = true
  try {
    const data = await shareApi.listAllSharesAdmin({
      page: pagination.value.page,
      page_size: pagination.value.page_size,
    })
    shares.value = data.items || []
    pagination.value = data.pagination || pagination.value
  } catch {
    shares.value = []
  } finally {
    loading.value = false
  }
}

function changePage(page) {
  pagination.value.page = page
  fetchShares()
}

async function toggleActive(item) {
  try {
    await shareApi.updateShare(item.id, { is_active: !item.is_active })
    appStore.showNotification(item.is_active ? '分享已关闭' : '分享已启用', 'success')
    fetchShares()
  } catch (e) {
    appStore.showNotification(e.message || '操作失败', 'error')
  }
}

async function handleDelete(item) {
  if (!confirm(`确定删除「${item.original_name}」？文件将同时被移除。`)) return
  try {
    await shareApi.deleteShare(item.id)
    appStore.showNotification('分享已删除', 'success')
    fetchShares()
  } catch (e) {
    appStore.showNotification(e.message || '删除失败', 'error')
  }
}

onMounted(fetchShares)
</script>
