<template>
  <MainLayout>
    <div class="max-w-4xl mx-auto">
      <h1 class="text-3xl font-bold mb-8">博客文章</h1>

      <!-- 分类 & 标签筛选（仅占位） -->
      <div class="flex flex-wrap gap-2 mb-8">
        <button v-for="cat in categories" :key="cat.id"
          @click="filterCategory = filterCategory === cat.id ? null : cat.id"
          class="px-3 py-1.5 text-sm rounded-full transition-colors"
          :class="filterCategory === cat.id ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'">
          {{ cat.name }}
        </button>
      </div>

      <!-- 文章列表 -->
      <div v-if="loading" class="text-center py-12 text-gray-400">加载中...</div>

      <div v-else-if="posts.length === 0" class="text-center py-12 text-gray-400">
        暂无文章
      </div>

      <div v-else class="space-y-6">
        <article v-for="post in posts" :key="post.id"
          class="bg-white rounded-xl border border-gray-100 p-6 hover:shadow-sm transition-shadow">
          <router-link :to="`/blog/${post.slug}`" class="block">
            <div class="flex items-start gap-4">
              <!-- 封面图 -->
              <img v-if="post.cover_image" :src="post.cover_image" alt=""
                class="w-24 h-24 object-cover rounded-lg flex-shrink-0" />

              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-2">
                  <h2 class="text-xl font-semibold text-gray-900 hover:text-primary-600 transition-colors truncate">
                    {{ post.title }}
                  </h2>
                  <span v-if="post.is_top" class="text-xs bg-red-100 text-red-600 px-2 py-0.5 rounded-full flex-shrink-0">置顶</span>
                </div>

                <p class="text-gray-500 text-sm mb-3 line-clamp-2">{{ post.summary || '暂无摘要' }}</p>

                <div class="flex items-center gap-3 text-xs text-gray-400">
                  <span v-if="post.category" class="bg-primary-50 text-primary-600 px-2 py-0.5 rounded-full">
                    {{ post.category.name }}
                  </span>
                  <span>{{ new Date(post.created_at).toLocaleDateString('zh-CN') }}</span>
                  <span>👁 {{ post.view_count }}</span>
                </div>

                <div v-if="post.tags && post.tags.length" class="flex gap-1.5 mt-2 flex-wrap">
                  <span v-for="tag in post.tags" :key="tag.id"
                    class="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded">
                    #{{ tag.name }}
                  </span>
                </div>
              </div>
            </div>
          </router-link>
        </article>
      </div>

      <!-- 分页 -->
      <div v-if="pagination.total_pages > 1" class="flex justify-center items-center gap-4 mt-8">
        <button :disabled="pagination.page <= 1" @click="changePage(pagination.page - 1)"
          class="px-4 py-2 text-sm bg-white border border-gray-200 rounded-lg disabled:opacity-50 hover:bg-gray-50 transition-colors">
          上一页
        </button>
        <span class="text-sm text-gray-500">{{ pagination.page }} / {{ pagination.total_pages }}</span>
        <button :disabled="pagination.page >= pagination.total_pages" @click="changePage(pagination.page + 1)"
          class="px-4 py-2 text-sm bg-white border border-gray-200 rounded-lg disabled:opacity-50 hover:bg-gray-50 transition-colors">
          下一页
        </button>
      </div>
    </div>
  </MainLayout>
</template>

<script setup>
/**
 * BlogList.vue —— 博客列表页
 * 分页展示文章，支持分类筛选
 */
import { ref, onMounted, watch } from 'vue'
import MainLayout from '@/layouts/MainLayout.vue'
import { blogApi } from '@/api/blog'

const posts = ref([])
const categories = ref([])
const loading = ref(true)
const filterCategory = ref(null)

const pagination = ref({
  page: 1,
  page_size: 10,
  total: 0,
  total_pages: 0,
})

async function fetchPosts() {
  loading.value = true
  try {
    const data = await blogApi.listPosts({
      page: pagination.value.page,
      page_size: pagination.value.page_size,
      category_id: filterCategory.value || undefined,
    })
    posts.value = data.items || []
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

// 监听分类筛选变化
watch(filterCategory, () => {
  pagination.value.page = 1
  fetchPosts()
})

onMounted(async () => {
  try {
    categories.value = await blogApi.listCategories()
  } catch {
    // 忽略
  }
  await fetchPosts()
})
</script>
