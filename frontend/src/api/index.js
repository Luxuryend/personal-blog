/**
 * Axios 实例 & 请求拦截器
 * - 自动附加 Authorization header
 * - 统一响应拦截：提取 data / 抛出错误
 */

import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

// 创建 Axios 实例，baseURL 为空则使用 Vite proxy
const http = axios.create({
  baseURL: '',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

// ── 请求拦截器 ─────────────────────────────────────────────
http.interceptors.request.use(
  (config) => {
    // 从 Pinia store 读取 token，自动附加到请求头
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

// ── 响应拦截器 ─────────────────────────────────────────────
http.interceptors.response.use(
  (response) => {
    // 统一响应按照 { code, data, message } 格式处理
    const res = response.data
    if (res.code !== 0) {
      // 业务错误
      const error = new Error(res.message || '请求失败')
      error.code = res.code
      return Promise.reject(error)
    }
    return res.data  // 直接返回 data 字段
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token 过期或未登录，清除本地状态并跳转登录页
      const authStore = useAuthStore()
      authStore.logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  },
)

export default http
