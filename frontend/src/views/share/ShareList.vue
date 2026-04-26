<template>
  <MainLayout>
    <div class="max-w-4xl mx-auto">
      <div class="flex items-center justify-between mb-8">
        <h1 class="text-3xl font-bold">文件分享</h1>
        <router-link v-if="authStore.isLoggedIn" to="/share/upload"
          class="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors text-sm">
          + 上传文件
        </router-link>
      </div>

      <div v-if="loading" class="text-center py-12 text-gray-400">加载中...</div>

      <div v-else-if="shares.length === 0" class="text-center py-12 text-gray-400">
        暂无分享文件
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="item in shares" :key="item.id"
          class="bg-white rounded-xl border border-gray-100 p-5 hover:shadow-sm transition-shadow">
          <router-link :to="`/share/${item.id}`" class="block">
            <!-- 图片预览 -->
            <div v-if="item.is_image" class="mb-3 bg-gray-50 rounded-lg overflow-hidden h-36 flex items-center justify-center">
              <img :src="`/uploads/${item.stored_path}`" alt=""
                class="max-w-full max-h-full object-cover" />
            </div>
            <div v-else class="mb-3 bg-gray-50 rounded-lg h-36 flex items-center justify-center">
              <svg class="w-12 h-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                  d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
            </div>

            <h3 class="font-medium text-gray-900 truncate">{{ item.original_name }}</h3>

            <div class="flex items-center justify-between mt-2 text-xs text-gray-400">
              <span>{{ formatSize(item.file_size) }}</span>
              <span>{{ new Date(item.created_at).toLocaleDateString('zh-CN') }}</span>
            </div>

            <div class="flex items-center gap-2 mt-2 text-xs text-gray-400">
              <span v-if="item.has_extract_code" class="text-amber-500">🔒 需提取码</span>
              <span v-else class="text-green-500">🔓 公开</span>
              <span v-if="item.expires_at" class="text-red-400">
                过期: {{ new Date(item.expires_at).toLocaleDateString('zh-CN') }}
              </span>
            </div>
          </router-link>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="pagination.total_pages > 1" class="flex justify-center items-center gap-4 mt-8">
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
/**
 * ShareList.vue —— 文件分享列表页
 */
import { ref, onMounted } from 'vue'
import MainLayout from '@/layouts/MainLayout.vue'
import { useAuthStore } from '@/stores/auth'
import { shareApi } from '@/api/share'

const authStore = useAuthStore()
const shares = ref([])
const loading = ref(true)
const pagination = ref({ page: 1, page_size: 12, total: 0, total_pages: 0 })

function formatSize(bytes) {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  let size = bytes
  while (size >= 1024 && i < units.length - 1) { size /= 1024; i++ }
  return `${size.toFixed(1)} ${units[i]}`
}

async function fetchShares() {
  loading.value = true
  try {
    const data = await shareApi.listShares({ page: pagination.value.page, page_size: pagination.value.page_size })
    // 注意：后端过滤了过期和无效的，直接取返回结果
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

onMounted(fetchShares)
</script>
