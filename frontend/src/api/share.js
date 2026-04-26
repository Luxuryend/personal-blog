/**
 * 文件分享 API
 */
import http from './index'

export const shareApi = {
  /** 上传文件 */
  uploadFile(formData, params) {
    return http.post('/api/share/upload', formData, {
      params,
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  /** 浏览分享列表 */
  listShares(params) {
    return http.get('/api/share/files', { params })
  },
  /** 管理员查看所有分享 */
  listAllSharesAdmin(params) {
    return http.get('/api/share/files/admin', { params })
  },
  /** 获取分享详情 */
  getShareDetail(id) {
    return http.get(`/api/share/files/${id}`)
  },
  /** 验证提取码 */
  verifyExtractCode(id, code) {
    return http.post(`/api/share/files/${id}/verify`, { extract_code: code })
  },
  /** 下载文件 */
  downloadFile(id, extractCode) {
    const params = extractCode ? { extract_code: extractCode } : {}
    return http.get(`/api/share/files/${id}/download`, { params })
  },
  /** 删除分享 */
  deleteShare(id) {
    return http.delete(`/api/share/files/${id}`)
  },
  /** 更新分享设置 */
  updateShare(id, data) {
    return http.put(`/api/share/files/${id}`, data)
  },
  /** 获取访问日志 */
  getAccessLogs(id, params) {
    return http.get(`/api/share/files/${id}/logs`, { params })
  },
}
