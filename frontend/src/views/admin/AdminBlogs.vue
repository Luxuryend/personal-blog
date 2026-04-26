<template>
  <MainLayout>
    <div class="max-w-5xl mx-auto">
      <div class="flex items-center justify-between mb-6">
        <div>
          <h1 class="text-3xl font-bold">博客管理</h1>
          <p class="text-sm text-gray-500 mt-1">共 {{ pagination.total }} 篇文章</p>
        </div>
        <router-link to="/blog/editor"
          class="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors text-sm">
          + 写文章
        </router-link>
      </div>

      <!-- 筛选 -->
      <div class="flex gap-2 mb-4">
        <button @click="filterPublished = null"
          class="px-3 py-1.5 text-sm rounded-full transition-colors"
          :class="filterPublished === null ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'">
          全部
        </button>
        <button @click="filterPublished = true"
          class="px-3 py-1.5 text-sm rounded-full transition-colors"
          :class="filterPublished === true ? 'bg-green-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'">
          已发布
        </button>
        <button @click="filterPublished = false"
          class="px-3 py-1.5 text-sm rounded-full transition-colors"
          :class="filterPublished === false ? 'bg-amber-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'">
          草稿
        </button>
      </div>

      <div v-if="loading" class="text-center py-12 text-gray-400">加载中...</div>

      <div v-else-if="posts.length === 0" class="text-center py-12 text-gray-400">暂无文章</div>

      <div v-else class="bg-white rounded-xl border border-gray-100 overflow-hidden">
        <table class="w-full">
          <thead class="bg-gray-50 border-b border-gray-100">
            <tr class="text-left text-sm text-gray-500">
              <th class="px-4 py-3 font-medium">标题</th>
              <th class="px-4 py-3 font-medium hidden md:table-cell">分类</th>
              <th class="px-4 py-3 font-medium hidden md:table-cell">状态</th>
              <th class="px-4 py-3 font-medium hidden sm:table-cell">浏览</th>
              <th class="px-4 py-3 font-medium hidden lg:table-cell">时间</th>
              <th class="px-4 py-3 font-medium text-right">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="post in posts" :key="post.id" class="hover:bg-gray-50/50 transition-colors">
              <td class="px-4 py-3">
                <router-link :to="`/blog/${post.slug}`" class="text-gray-900 hover:text-primary-600 font-medium">
                  {{ post.title }}
                </router-link>
                <span v-if="post.is_top" class="ml-2 text-xs bg-red-100 text-red-600 px-1.5 py-0.5 rounded">置顶</span>
              </td>
              <td class="px-4 py-3 text-sm text-gray-500 hidden md:table-cell">
                {{ post.category?.name || '-' }}
              </td>
              <td class="px-4 py-3 hidden md:table-cell">
                <span :class="post.is_published ? 'bg-green-100 text-green-600' : 'bg-amber-100 text-amber-600'"
                  class="text-xs px-2 py-0.5 rounded-full">
                  {{ post.is_published ? '已发布' : '草稿' }}
                </span>
              </td>
              <td class="px-4 py-3 text-sm text-gray-500 hidden sm:table-cell">{{ post.view_count }}</td>
              <td class="px-4 py-3 text-sm text-gray-500 hidden lg:table-cell">
                {{ new Date(post.created_at).toLocaleDateString('zh-CN') }}
              </td>
              <td class="px-4 py-3 text-right">
                <div class="flex items-center justify-end gap-2">
                  <router-link :to="`/blog/editor/${post.id}`"
                    class="text-xs text-primary-600 hover:text-primary-700 px-2 py-1">
                    编辑
                  </router-link>
                  <button @click="handleDelete(post)"
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
import { ref, onMounted, watch } from 'vue'
import MainLayout from '@/layouts/MainLayout.vue'
import { blogApi } from '@/api/blog'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()
const posts = ref([])
const loading = ref(true)
const filterPublished = ref(null)
const pagination = ref({ page: 1, page_size: 20, total: 0, total_pages: 0 })

async function fetchPosts() {
  loading.value = true
  try {
    const data = await blogApi.listAllPostsAdmin({
      page: pagination.value.page,
      page_size: pagination.value.page_size,
    })
    // 前端过滤已发布/草稿
    let items = data.items || []
    if (filterPublished.value === true) items = items.filter(p => p.is_published)
    else if (filterPublished.value === false) items = items.filter(p => !p.is_published)
    posts.value = items
    pagination.value = data.pagination || pagination.value
  } catch {
    posts.value = []
  } finally {
    loading.value = false
  }
}

function changePage(page) {
  pagination.value.page = page
  fetchPosts()
}

watch(filterPublished, () => {
  pagination.value.page = 1
  fetchPosts()
})

async function handleDelete(post) {
  if (!confirm(`确定删除「${post.title}」？此操作不可撤销。`)) return
  try {
    await blogApi.deletePost(post.id)
    appStore.showNotification('文章已删除', 'success')
    fetchPosts()
  } catch (e) {
    appStore.showNotification(e.message || '删除失败', 'error')
  }
}

onMounted(fetchPosts)
</script>
