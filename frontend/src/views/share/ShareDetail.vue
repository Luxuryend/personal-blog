<template>
  <MainLayout>
    <div class="max-w-xl mx-auto">
      <div v-if="loading" class="text-center py-12 text-gray-400">加载中...</div>

      <div v-else-if="!share" class="text-center py-12 text-gray-400">分享不存在或已失效</div>

      <template v-else>
        <div class="bg-white rounded-xl border border-gray-100 p-8">
          <!-- 图片预览 -->
          <div v-if="share.is_image" class="mb-6 bg-gray-50 rounded-lg overflow-hidden flex items-center justify-center max-h-80">
            <img :src="`/uploads/${share.stored_path}`" alt=""
              class="max-w-full max-h-80 object-contain" />
          </div>

          <div v-else class="mb-6 bg-gray-50 rounded-lg h-40 flex items-center justify-center">
            <svg class="w-16 h-16 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
          </div>

          <!-- 文件信息 -->
          <h2 class="text-xl font-semibold mb-4">{{ share.original_name }}</h2>

          <div class="space-y-2 text-sm text-gray-500 mb-6">
            <div class="flex justify-between">
              <span>文件大小</span>
              <span>{{ formatSize(share.file_size) }}</span>
            </div>
            <div class="flex justify-between">
              <span>文件类型</span>
              <span>{{ share.file_type || '未知' }}</span>
            </div>
            <div class="flex justify-between">
              <span>上传时间</span>
              <span>{{ new Date(share.created_at).toLocaleString('zh-CN') }}</span>
            </div>
            <div v-if="share.expires_at" class="flex justify-between text-red-400">
              <span>过期时间</span>
              <span>{{ new Date(share.expires_at).toLocaleString('zh-CN') }}</span>
            </div>
            <div class="flex justify-between">
              <span>下载次数</span>
              <span>{{ share.download_count }}{{ share.max_downloads ? ` / ${share.max_downloads}` : '' }}</span>
            </div>
          </div>

          <!-- 提取码输入 -->
          <div v-if="share.has_extract_code && !verified" class="mb-4">
            <div class="flex gap-2">
              <input v-model="codeInput" type="text" maxlength="10" placeholder="请输入提取码"
                class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none" />
              <button @click="verifyCode"
                class="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700 transition-colors text-sm">
                验证
              </button>
            </div>
            <p v-if="codeError" class="text-red-500 text-xs mt-1">{{ codeError }}</p>
          </div>

          <!-- 下载按钮 -->
          <a v-if="!share.has_extract_code || verified"
            :href="`/api/share/files/${share.id}/download`"
            class="block w-full bg-primary-600 text-white text-center py-3 rounded-lg hover:bg-primary-700 transition-colors font-medium">
            📥 下载文件
          </a>

          <!-- 管理员操作 -->
          <div v-if="authStore.isAdmin" class="mt-4 pt-4 border-t border-gray-100">
            <button @click="handleDelete" class="text-sm text-red-500 hover:text-red-600">
              删除此分享
            </button>
          </div>
        </div>
      </template>
    </div>
  </MainLayout>
</template>

<script setup>
/**
 * ShareDetail.vue —— 分享详情页
 * 支持提取码验证和文件下载
 */
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'
import { shareApi } from '@/api/share'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const appStore = useAppStore()

const share = ref(null)
const loading = ref(true)
const verified = ref(false)
const codeInput = ref('')
const codeError = ref('')

function formatSize(bytes) {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  let size = bytes
  while (size >= 1024 && i < units.length - 1) { size /= 1024; i++ }
  return `${size.toFixed(1)} ${units[i]}`
}

async function verifyCode() {
  codeError.value = ''
  try {
    const data = await shareApi.verifyExtractCode(route.params.id, codeInput.value)
    verified.value = true
    share.value = data
  } catch (e) {
    codeError.value = e.message || '提取码错误'
  }
}

async function handleDelete() {
  if (!confirm('确定删除此分享？')) return
  try {
    await shareApi.deleteShare(route.params.id)
    appStore.showNotification('分享已删除', 'success')
    router.push('/share')
  } catch (e) {
    appStore.showNotification(e.message || '删除失败', 'error')
  }
}

onMounted(async () => {
  try {
    const data = await shareApi.getShareDetail(route.params.id)
    share.value = data
    if (!share.value.has_extract_code) {
      verified.value = true
    }
  } catch {
    share.value = null
  } finally {
    loading.value = false
  }
})
</script>
