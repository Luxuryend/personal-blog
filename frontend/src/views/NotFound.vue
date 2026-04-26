<template>
  <MainLayout>
    <div class="text-center py-24">
      <h1 class="text-6xl font-bold text-gray-200 mb-4">404</h1>
      <p class="text-xl text-gray-600 mb-8">页面不存在</p>
      <router-link to="/" class="bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 transition-colors">
        返回首页
      </router-link>
    </div>
  </MainLayout>
</template>

<script setup>
import MainLayout from '@/layouts/MainLayout.vue'
</script>
