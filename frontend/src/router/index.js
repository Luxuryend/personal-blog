/**
 * Vue Router 配置
 * 定义前端路由与对应视图组件
 */

import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '首页' },
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' },
  },
  // ── 博客 ────────────────────────────────────────────────
  {
    path: '/blog',
    name: 'BlogList',
    component: () => import('@/views/blog/BlogList.vue'),
    meta: { title: '博客' },
  },
  {
    path: '/blog/:slug',
    name: 'BlogDetail',
    component: () => import('@/views/blog/BlogDetail.vue'),
    meta: { title: '文章详情' },
  },
  {
    path: '/blog/editor/:id?',
    name: 'BlogEditor',
    component: () => import('@/views/blog/BlogEditor.vue'),
    meta: { title: '编辑文章', requiresAuth: true },
  },
  // ── 文件分享 ────────────────────────────────────────────
  {
    path: '/share',
    name: 'ShareList',
    component: () => import('@/views/share/ShareList.vue'),
    meta: { title: '文件分享' },
  },
  {
    path: '/share/upload',
    name: 'ShareUpload',
    component: () => import('@/views/share/ShareUpload.vue'),
    meta: { title: '上传分享', requiresAuth: true },
  },
  {
    path: '/share/:id',
    name: 'ShareDetail',
    component: () => import('@/views/share/ShareDetail.vue'),
    meta: { title: '分享详情' },
  },
  // ── 留言板 ──────────────────────────────────────────────
  {
    path: '/guestbook',
    name: 'Guestbook',
    component: () => import('@/views/guestbook/Guestbook.vue'),
    meta: { title: '留言板' },
  },
  // ── 管理后台 ────────────────────────────────────────────
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: () => import('@/views/admin/AdminDashboard.vue'),
    meta: { title: '管理后台', requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/admin/blogs',
    name: 'AdminBlogs',
    component: () => import('@/views/admin/AdminBlogs.vue'),
    meta: { title: '博客管理', requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/admin/shares',
    name: 'AdminShares',
    component: () => import('@/views/admin/AdminShares.vue'),
    meta: { title: '分享管理', requiresAuth: true, requiresAdmin: true },
  },
  // ── 个人设置 ────────────────────────────────────────────
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: { title: '个人设置', requiresAuth: true },
  },
  // ── 404 ─────────────────────────────────────────────────
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: '404' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  // 滚动行为：切换页面时回到顶部
  scrollBehavior() {
    return { top: 0 }
  },
})

// ── 路由守卫 ───────────────────────────────────────────────
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = `${to.meta.title || '个人网站'} | MySite`

  // 需要登录的路由检查
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('token')
    if (!token) {
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
  }

  // 需要管理员权限的路由检查
  if (to.meta.requiresAdmin) {
    const role = localStorage.getItem('user_role')
    if (role !== 'admin') {
      next({ name: 'Home' })
      return
    }
  }

  next()
})

export default router
