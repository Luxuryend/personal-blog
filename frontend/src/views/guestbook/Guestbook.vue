<template>
  <MainLayout>
    <div class="max-w-3xl mx-auto">
      <h1 class="text-3xl font-bold mb-8">留言板</h1>

      <!-- 留言表单 -->
      <div class="bg-white rounded-xl border border-gray-100 p-6 mb-8">
        <h2 class="text-lg font-semibold mb-4">写下你想说的</h2>
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div>
            <textarea v-model="form.content" rows="4" required maxlength="5000" placeholder="说点什么..."
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none resize-none"></textarea>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
            <input v-if="!authStore.isAdmin" v-model="form.nickname" type="text" placeholder="昵称（默认匿名）" maxlength="50"
              class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none text-sm" />
            <input v-else type="text" value="admin" disabled
              class="px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500 outline-none text-sm" />
            <input v-model="form.email" type="email" placeholder="邮箱（不公开）" maxlength="200"
              class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none text-sm" />
            <input v-model="form.website" type="url" placeholder="个人网站（选填）" maxlength="500"
              class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none text-sm" />
          </div>
          <button type="submit" :disabled="submitting"
            class="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors text-sm">
            {{ submitting ? '提交中...' : '发布留言' }}
          </button>
          <p v-if="submitMsg" class="text-sm" :class="submitMsgType === 'success' ? 'text-green-600' : 'text-red-500'">
            {{ submitMsg }}
          </p>
        </form>
      </div>

      <!-- 留言列表 -->
      <div v-if="loading" class="text-center py-8 text-gray-400">加载中...</div>

      <div v-else-if="messages.length === 0" class="text-center py-8 text-gray-400">
        还没有留言，来写下第一条吧
      </div>

      <div v-else class="space-y-4">
        <div v-for="msg in messages" :key="msg.id" class="bg-white rounded-xl border border-gray-100 p-6">
          <!-- 主留言 -->
          <div class="flex items-start justify-between mb-2">
            <div>
              <span class="font-medium text-gray-900">{{ msg.nickname }}</span>
              <span v-if="msg.website" class="ml-2">
                <a :href="msg.website" target="_blank" rel="noopener noreferrer" class="text-primary-600 hover:text-primary-700 text-sm">🌐</a>
              </span>
              <span class="ml-2 text-xs text-gray-400">{{ new Date(msg.created_at).toLocaleString('zh-CN') }}</span>
            </div>
            <div class="flex items-center gap-2">
              <button v-if="authStore.isAdmin" @click="showReplyForm(msg.id)" class="text-xs text-gray-400 hover:text-primary-600">
                回复
              </button>
              <button v-if="authStore.isAdmin" @click="handleDeleteMessage(msg.id, msg.nickname)" class="text-xs text-red-400 hover:text-red-600">
                删除
              </button>
            </div>
          </div>
          <p class="text-gray-700 whitespace-pre-wrap">{{ msg.content }}</p>

          <!-- 回复列表 -->
          <div v-if="msg.replies && msg.replies.length" class="mt-4 ml-6 space-y-3">
            <div v-for="reply in msg.replies" :key="reply.id"
              class="bg-gray-50 rounded-lg p-4 border-l-2 border-primary-200">
              <div class="flex items-center gap-2 mb-1">
                <span class="font-medium text-sm" :class="reply.is_admin_reply ? 'text-primary-600' : 'text-gray-900'">
                  {{ reply.is_admin_reply ? '管理员' : reply.nickname }}
                </span>
                <span class="text-xs text-gray-400">{{ new Date(reply.created_at).toLocaleString('zh-CN') }}</span>
                <button v-if="authStore.isAdmin" @click="handleDeleteMessage(reply.id, '回复')" class="text-xs text-red-400 hover:text-red-600 ml-auto">
                  删除
                </button>
              </div>
              <p class="text-sm text-gray-700">{{ reply.content }}</p>
            </div>
          </div>

          <!-- 回复表单 -->
          <div v-if="replyToId === msg.id" class="mt-4 ml-6">
            <form @submit.prevent="handleReply(msg.id)" class="flex gap-2">
              <input v-model="replyContent" type="text" placeholder="写下你的回复..." required
                class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none text-sm" />
              <button type="submit" :disabled="replying"
                class="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 disabled:opacity-50 text-sm">
                回复
              </button>
            </form>
          </div>
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
 * Guestbook.vue —— 留言板页面
 * 支持留言、回复、分页查看
 */
import { ref, onMounted } from 'vue'
import MainLayout from '@/layouts/MainLayout.vue'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'
import { guestbookApi } from '@/api/guestbook'

const authStore = useAuthStore()
const appStore = useAppStore()

const messages = ref([])
const loading = ref(true)
const submitting = ref(false)
const submitMsg = ref('')
const submitMsgType = ref('')
const pagination = ref({ page: 1, page_size: 20, total: 0, total_pages: 0 })

// 留言表单
const form = ref({ content: '', nickname: '', email: '', website: '' })

// 回复
const replyToId = ref(null)
const replyContent = ref('')
const replying = ref(false)

async function fetchMessages() {
  loading.value = true
  try {
    const data = await guestbookApi.listMessages({ page: pagination.value.page, page_size: pagination.value.page_size })
    messages.value = data.items || []
    pagination.value = data.pagination || pagination.value
  } catch {
    messages.value = []
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  submitting.value = true
  submitMsg.value = ''
  try {
    await guestbookApi.createMessage(form.value)
    submitMsg.value = '留言已提交，审核通过后将对外显示'
    submitMsgType.value = 'success'
    form.value = { content: '', nickname: '', email: '', website: '' }
    fetchMessages()
  } catch (e) {
    submitMsg.value = e.message || '提交失败'
    submitMsgType.value = 'error'
  } finally {
    submitting.value = false
  }
}

function showReplyForm(msgId) {
  replyToId.value = replyToId.value === msgId ? null : msgId
  replyContent.value = ''
}

async function handleReply(parentId) {
  replying.value = true
  try {
    await guestbookApi.createAdminReply({
      content: replyContent.value,
      parent_id: parentId,
    })
    appStore.showNotification('回复成功', 'success')
    replyToId.value = null
    replyContent.value = ''
    fetchMessages()
  } catch (e) {
    appStore.showNotification(e.message || '回复失败', 'error')
  } finally {
    replying.value = false
  }
}

async function handleDeleteMessage(id, label) {
  if (!confirm(`确定删除「${label}」的这条留言？`)) return
  try {
    await guestbookApi.deleteMessage(id)
    appStore.showNotification('留言已删除', 'success')
    fetchMessages()
  } catch (e) {
    appStore.showNotification(e.message || '删除失败', 'error')
  }
}

function changePage(page) {
  pagination.value.page = page
  fetchMessages()
}

onMounted(fetchMessages)
</script>
