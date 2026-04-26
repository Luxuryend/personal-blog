<template>
  <MainLayout>
    <div class="text-center py-16">
      <!-- 欢迎区 -->
      <h1 class="text-4xl font-bold text-gray-900 mb-4">欢迎来到我的个人网站</h1>
      <p class="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
        这里是我的数字花园 —— 记录技术思考、分享有趣的文件、与朋友们交流。
      </p>

      <!-- 快捷入口卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto mt-12">
        <router-link to="/blog"
          class="block p-8 bg-white rounded-xl shadow-sm border border-gray-100 hover:shadow-md hover:border-primary-200 transition-all group">
          <div class="text-4xl mb-4 text-primary-500 group-hover:scale-110 transition-transform">📝</div>
          <h2 class="text-xl font-semibold mb-2">博客</h2>
          <p class="text-gray-500 text-sm">技术文章、项目经验、生活随笔</p>
        </router-link>

        <router-link to="/share"
          class="block p-8 bg-white rounded-xl shadow-sm border border-gray-100 hover:shadow-md hover:border-primary-200 transition-all group">
          <div class="text-4xl mb-4 text-primary-500 group-hover:scale-110 transition-transform">📁</div>
          <h2 class="text-xl font-semibold mb-2">文件分享</h2>
          <p class="text-gray-500 text-sm">图片、文档、资源文件分享</p>
        </router-link>

        <router-link to="/guestbook"
          class="block p-8 bg-white rounded-xl shadow-sm border border-gray-100 hover:shadow-md hover:border-primary-200 transition-all group">
          <div class="text-4xl mb-4 text-primary-500 group-hover:scale-110 transition-transform">💬</div>
          <h2 class="text-xl font-semibold mb-2">留言板</h2>
          <p class="text-gray-500 text-sm">留下你的想法和建议</p>
        </router-link>
      </div>

      <!-- 最新博客预览 -->
      <div class="mt-16 text-left max-w-4xl mx-auto">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-2xl font-bold text-gray-900">最新文章</h3>
          <router-link to="/blog" class="text-primary-600 hover:text-primary-700 text-sm">查看全部 →</router-link>
        </div>

        <div v-if="loading" class="text-center py-8 text-gray-400">加载中...</div>

        <div v-else-if="posts.length === 0" class="text-center py-8 text-gray-400">
          还没有文章，敬请期待
        </div>

        <div v-else class="space-y-4">
          <article v-for="post in posts" :key="post.id"
            class="p-6 bg-white rounded-lg border border-gray-100 hover:border-primary-100 transition-colors">
            <router-link :to="`/blog/${post.slug}`" class="block">
              <div class="flex items-start justify-between">
                <div>
                  <h4 class="text-lg font-semibold text-gray-900 hover:text-primary-600 transition-colors">{{ post.title }}</h4>
                  <p class="text-sm text-gray-500 mt-1">{{ post.summary || '暂无摘要' }}</p>
                </div>
                <span v-if="post.category" class="text-xs bg-primary-50 text-primary-600 px-2 py-1 rounded-full whitespace-nowrap ml-4">
                  {{ post.category.name }}
                </span>
              </div>
              <div class="flex items-center gap-4 mt-3 text-xs text-gray-400">
                <span>{{ new Date(post.created_at).toLocaleDateString('zh-CN') }}</span>
                <span>👁 {{ post.view_count }}</span>
              </div>
            </router-link>
          </article>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup>
/**
 * Home.vue —— 首页
 * 展示欢迎信息和最新博客文章
 */
import { ref, onMounted } from 'vue'
import MainLayout from '@/layouts/MainLayout.vue'
import { blogApi } from '@/api/blog'

const posts = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const data = await blogApi.listPosts({ page: 1, page_size: 5 })
    posts.value = data.items || []
  } catch {
    // 静默处理
  } finally {
    loading.value = false
  }
})
</script>
