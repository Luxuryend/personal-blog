/**
 * 认证 API
 */
import http from './index'

export const authApi = {
  /** 登录 */
  login(username, password) {
    return http.post('/api/auth/login', { username, password })
  },
  /** 获取当前用户信息 */
  getMe() {
    return http.get('/api/auth/me')
  },
  /** 注册 */
  register(data) {
    return http.post('/api/auth/register', data)
  },
  /** 更新个人信息 */
  updateMe(data) {
    return http.put('/api/auth/me', data)
  },
}
