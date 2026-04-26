/**
 * 认证状态管理
 * 管理登录状态、用户信息、Token 持久化
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  // ── 状态 ────────────────────────────────────────────────
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)

  // ── 计算属性 ────────────────────────────────────────────
  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  // ── 操作 ────────────────────────────────────────────────

  /** 登录 */
  async function login(username, password) {
    const data = await authApi.login(username, password)
    token.value = data.access_token
    user.value = data.user
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('user_role', data.user.role)
    return data
  }

  /** 退出登录 */
  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user_role')
  }

  /** 从 localStorage 恢复会话 */
  async function restoreSession() {
    if (!token.value) return
    try {
      user.value = await authApi.getMe()
      localStorage.setItem('user_role', user.value.role)
    } catch {
      // Token 无效，清除
      logout()
    }
  }

  return {
    token,
    user,
    isLoggedIn,
    isAdmin,
    login,
    logout,
    restoreSession,
  }
})
