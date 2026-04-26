/**
 * 留言板 API
 */
import http from './index'

export const guestbookApi = {
  /** 获取已审核留言 */
  listMessages(params) {
    return http.get('/api/guestbook/messages', { params })
  },
  /** 管理员查看全部留言 */
  listAllMessagesAdmin(params) {
    return http.get('/api/guestbook/messages/admin', { params })
  },
  /** 创建留言/回复 */
  createMessage(data) {
    return http.post('/api/guestbook/messages', data)
  },
  /** 管理员回复 */
  createAdminReply(data) {
    return http.post('/api/guestbook/messages/admin', data)
  },
  /** 审核留言 */
  reviewMessage(id, data) {
    return http.put(`/api/guestbook/messages/${id}/review`, data)
  },
  /** 删除留言 */
  deleteMessage(id) {
    return http.delete(`/api/guestbook/messages/${id}`)
  },
}
