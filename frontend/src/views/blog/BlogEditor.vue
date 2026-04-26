<template>
  <MainLayout>
    <div class="max-w-4xl mx-auto">
      <h1 class="text-2xl font-bold mb-6">{{ isEdit ? '编辑文章' : '写文章' }}</h1>

      <form @submit.prevent="handleSave" class="space-y-6">
        <!-- 标题 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">标题</label>
          <input v-model="form.title" type="text" required
            class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none text-lg" />
        </div>

        <!-- Slug -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">URL 标识 (slug)</label>
          <input v-model="form.slug" type="text" required pattern="^[a-z0-9\-]+$"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
            placeholder="my-article-title" />
        </div>

        <!-- 分类 & 标签 & 选项 -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">分类</label>
            <select v-model="form.category_id"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none">
              <option :value="null">无分类</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">标签</label>
            <div class="flex flex-wrap gap-1.5 p-2 border border-gray-300 rounded-lg min-h-[42px]">
              <span v-for="tag in selectedTags" :key="tag.id"
                class="text-xs bg-primary-50 text-primary-600 px-2 py-0.5 rounded-full flex items-center gap-1">
                {{ tag.name }}
                <button type="button" @click="removeTag(tag)" class="hover:text-red-500">×</button>
              </span>
              <select v-model="newTagId" @change="addTag"
                class="text-sm border-none outline-none bg-transparent text-gray-400">
                <option value="">+ 添加标签</option>
                <option v-for="tag in availableTags" :key="tag.id" :value="tag.id">{{ tag.name }}</option>
              </select>
            </div>
          </div>

          <div class="flex items-end gap-4">
            <label class="flex items-center gap-2 text-sm">
              <input v-model="form.is_published" type="checkbox" class="rounded" />
              发布
            </label>
            <label class="flex items-center gap-2 text-sm">
              <input v-model="form.is_top" type="checkbox" class="rounded" />
              置顶
            </label>
          </div>
        </div>

        <!-- 摘要 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">摘要</label>
          <textarea v-model="form.summary" rows="2"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none resize-none"></textarea>
        </div>

        <!-- Markdown 编辑器（简易 textarea） -->
        <div>
          <div class="flex items-center justify-between mb-1">
            <label class="text-sm font-medium text-gray-700">正文 (Markdown)</label>
            <span class="text-xs text-gray-400">支持 Markdown 语法</span>
          </div>
          <textarea v-model="form.content" rows="20" required
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none font-mono text-sm leading-relaxed resize-y"></textarea>
        </div>

        <!-- 预览 -->
        <div v-if="form.content" class="border border-gray-200 rounded-lg p-6">
          <h3 class="text-sm font-medium text-gray-700 mb-2">预览</h3>
          <div class="markdown-body" v-html="previewContent"></div>
        </div>

        <!-- 操作按钮 -->
        <div class="flex gap-3">
          <button type="submit" :disabled="saving"
            class="bg-primary-600 text-white px-6 py-2.5 rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors font-medium">
            {{ saving ? '保存中...' : '保存' }}
          </button>
          <router-link to="/blog"
            class="px-6 py-2.5 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-gray-600">
            取消
          </router-link>
        </div>
      </form>
    </div>
  </MainLayout>
</template>

<script setup>
/**
 * BlogEditor.vue —— 博客编辑器
 * 支持创建和编辑文章（简易 textarea，可替换为富文本编辑器）
 */
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marked } from 'marked'
import MainLayout from '@/layouts/MainLayout.vue'
import { blogApi } from '@/api/blog'
import { useAppStore } from '@/stores/app'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()

const isEdit = computed(() => !!route.params.id)
const saving = ref(false)

const form = ref({
  title: '',
  slug: '',
  content: '',
  summary: '',
  is_published: false,
  is_top: false,
  category_id: null,
})

const categories = ref([])
const allTags = ref([])
const selectedTags = ref([])
const newTagId = ref('')

const availableTags = computed(() =>
  allTags.value.filter(t => !selectedTags.value.find(s => s.id === t.id))
)

const previewContent = computed(() => {
  if (!form.value.content) return ''
  return marked(form.value.content, { breaks: true })
})

function addTag() {
  if (!newTagId.value) return
  const tag = allTags.value.find(t => t.id === Number(newTagId.value))
  if (tag && !selectedTags.value.find(s => s.id === tag.id)) {
    selectedTags.value.push(tag)
  }
  newTagId.value = ''
}

function removeTag(tag) {
  selectedTags.value = selectedTags.value.filter(t => t.id !== tag.id)
}

async function handleSave() {
  saving.value = true
  try {
    const data = {
      ...form.value,
      tag_ids: selectedTags.value.map(t => t.id),
    }

    if (isEdit.value) {
      await blogApi.updatePost(route.params.id, data)
      appStore.showNotification('文章已更新', 'success')
    } else {
      const post = await blogApi.createPost(data)
      appStore.showNotification('文章已创建', 'success')
      router.push(`/blog/${post.slug}`)
      return
    }
    router.push('/blog')
  } catch (e) {
    appStore.showNotification(e.message || '保存失败', 'error')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    categories.value = await blogApi.listCategories()
    allTags.value = await blogApi.listTags()
  } catch {
    // 忽略
  }

  if (isEdit.value) {
    try {
      const post = await blogApi.getPost(route.params.id)
      form.value = {
        title: post.title,
        slug: post.slug,
        content: post.content,
        summary: post.summary || '',
        is_published: post.is_published,
        is_top: post.is_top,
        category_id: post.category?.id || null,
      }
      selectedTags.value = post.tags || []
    } catch {
      appStore.showNotification('文章不存在', 'error')
      router.push('/blog')
    }
  }
})
</script>
