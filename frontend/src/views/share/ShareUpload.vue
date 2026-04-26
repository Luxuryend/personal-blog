<template>
  <MainLayout>
    <div class="max-w-xl mx-auto">
      <h1 class="text-2xl font-bold mb-6">上传文件</h1>

      <form @submit.prevent="handleUpload" class="space-y-6 bg-white p-8 rounded-xl border border-gray-100">
        <!-- 文件选择 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">选择文件</label>
          <div @drop.prevent="onDrop" @dragover.prevent
            class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary-400 transition-colors cursor-pointer"
            @click="$refs.fileInput.click()">
            <div v-if="!selectedFile" class="text-gray-400">
              <svg class="w-10 h-10 mx-auto mb-2 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <p>拖拽文件到此处，或点击选择</p>
              <p class="text-xs mt-1">支持图片、文档、压缩包等常见格式</p>
            </div>
            <div v-else>
              <p class="text-primary-600 font-medium">{{ selectedFile.name }}</p>
              <p class="text-xs text-gray-400 mt-1">{{ formatSize(selectedFile.size) }}</p>
            </div>
            <input ref="fileInput" type="file" class="hidden" @change="onFileChange" />
          </div>
        </div>

        <!-- 提取码 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">提取码（选填）</label>
          <input v-model="extractCode" type="text" maxlength="10"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
            placeholder="留空则无需提取码" />
        </div>

        <!-- 过期时间 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">过期时间（选填）</label>
          <input v-model="expiresAt" type="datetime-local"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none" />
        </div>

        <!-- 下载次数限制 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">最大下载次数（选填）</label>
          <input v-model.number="maxDownloads" type="number" min="1"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
            placeholder="留空则不限制" />
        </div>

        <div v-if="errorMsg" class="text-red-500 text-sm bg-red-50 px-3 py-2 rounded-lg">
          {{ errorMsg }}
        </div>

        <button type="submit" :disabled="uploading || !selectedFile"
          class="w-full bg-primary-600 text-white py-2.5 rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium">
          {{ uploading ? '上传中...' : '上传' }}
        </button>
      </form>
    </div>
  </MainLayout>
</template>

<script setup>
/**
 * ShareUpload.vue —— 文件上传页面
 */
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'
import { shareApi } from '@/api/share'
import { useAppStore } from '@/stores/app'

const router = useRouter()
const appStore = useAppStore()

const selectedFile = ref(null)
const extractCode = ref('')
const expiresAt = ref('')
const maxDownloads = ref(null)
const uploading = ref(false)
const errorMsg = ref('')

function formatSize(bytes) {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  let size = bytes
  while (size >= 1024 && i < units.length - 1) { size /= 1024; i++ }
  return `${size.toFixed(1)} ${units[i]}`
}

function onFileChange(e) {
  const file = e.target.files?.[0]
  if (file) selectedFile.value = file
}

function onDrop(e) {
  const file = e.dataTransfer.files?.[0]
  if (file) selectedFile.value = file
}

async function handleUpload() {
  if (!selectedFile.value) return
  uploading.value = true
  errorMsg.value = ''

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)

    const params = {}
    if (extractCode.value) params.extract_code = extractCode.value
    if (expiresAt.value) params.expires_at = new Date(expiresAt.value).toISOString()
    if (maxDownloads.value) params.max_downloads = maxDownloads.value

    await shareApi.uploadFile(formData, params)
    appStore.showNotification('文件上传成功', 'success')
    router.push('/share')
  } catch (e) {
    errorMsg.value = e.message || '上传失败'
  } finally {
    uploading.value = false
  }
}
</script>
