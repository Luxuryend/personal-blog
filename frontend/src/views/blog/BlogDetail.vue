<template>
  <MainLayout>
    <div class="max-w-3xl mx-auto">
      <div v-if="loading" class="text-center py-12 text-gray-400">加载中...</div>

      <div v-else-if="!post" class="text-center py-12 text-gray-400">文章不存在</div>

      <template v-else>
        <!-- 文章头部 -->
        <div class="mb-8">
          <h1 class="text-3xl font-bold text-gray-900 mb-4">{{ post.title }}</h1>

          <div class="flex items-center gap-4 text-sm text-gray-500 mb-4">
            <span>{{ new Date(post.created_at).toLocaleDateString('zh-CN') }}</span>
            <span>👁 {{ post.view_count }}</span>
            <span v-if="post.category" class="bg-primary-50 text-primary-600 px-2 py-0.5 rounded-full">
              {{ post.category.name }}
            </span>
          </div>

          <div v-if="post.tags && post.tags.length" class="flex gap-2 flex-wrap mb-4">
            <span v-for="tag in post.tags" :key="tag.id"
              class="text-xs bg-gray-100 text-gray-500 px-2.5 py-1 rounded-full">
              #{{ tag.name }}
            </span>
          </div>
        </div>

        <!-- 封面图 -->
        <img v-if="post.cover_image" :src="post.cover_image" alt="cover"
          class="w-full h-64 object-cover rounded-xl mb-8" />

        <!-- Markdown 正文 -->
        <div class="markdown-body bg-white p-8 rounded-xl border border-gray-100 mb-8" v-html="renderedContent"></div>

        <!-- 编辑按钮（管理员） -->
        <div v-if="authStore.isAdmin" class="flex justify-center items-center gap-4 mb-8">
          <router-link :to="`/blog/editor/${post.id}`"
            class="text-sm text-primary-600 hover:text-primary-700">
            ✏️ 编辑此文章
          </router-link>
          <span class="text-gray-300">|</span>
          <button @click="handleDelete" class="text-sm text-red-500 hover:text-red-600">
            🗑 删除此文章
          </button>
        </div>
      </template>
    </div>
  </MainLayout>
</template>

<script setup>
/**
 * BlogDetail.vue —— 文章详情页
 * 使用 marked 将 Markdown 渲染为 HTML
 */
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marked } from 'marked'
import MainLayout from '@/layouts/MainLayout.vue'
import { blogApi } from '@/api/blog'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const appStore = useAppStore()

const post = ref(null)
const loading = ref(true)

const renderedContent = computed(() => {
  if (!post.value?.content) return ''
  return marked(post.value.content, { breaks: true })
})

async function handleDelete() {
  if (!post.value) return
  if (!confirm(`确定删除「${post.value.title}」？此操作不可撤销。`)) return
  try {
    await blogApi.deletePost(post.value.id)
    appStore.showNotification('文章已删除', 'success')
    router.push('/blog')
  } catch (e) {
    appStore.showNotification(e.message || '删除失败', 'error')
  }
}

onMounted(async () => {
  try {
    post.value = await blogApi.getPost(route.params.slug)
  } catch {
    post.value = null
  } finally {
    loading.value = false
  }
})
</script>
