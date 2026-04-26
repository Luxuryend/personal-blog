/**
 * 博客 API
 */
import http from './index'

export const blogApi = {
  /** 获取文章列表 */
  listPosts(params) {
    return http.get('/api/blog/posts', { params })
  },
  /** 管理员获取全部文章 */
  listAllPostsAdmin(params) {
    return http.get('/api/blog/posts/admin', { params })
  },
  /** 获取文章详情 */
  getPost(slugOrId) {
    return http.get(`/api/blog/posts/${slugOrId}`)
  },
  /** 创建文章 */
  createPost(data) {
    return http.post('/api/blog/posts', data)
  },
  /** 更新文章 */
  updatePost(id, data) {
    return http.put(`/api/blog/posts/${id}`, data)
  },
  /** 删除文章 */
  deletePost(id) {
    return http.delete(`/api/blog/posts/${id}`)
  },
  /** 获取分类列表 */
  listCategories() {
    return http.get('/api/blog/categories')
  },
  /** 创建分类 */
  createCategory(data) {
    return http.post('/api/blog/categories', data)
  },
  /** 删除分类 */
  deleteCategory(id) {
    return http.delete(`/api/blog/categories/${id}`)
  },
  /** 获取标签列表 */
  listTags() {
    return http.get('/api/blog/tags')
  },
  /** 创建标签 */
  createTag(data) {
    return http.post('/api/blog/tags', data)
  },
  /** 删除标签 */
  deleteTag(id) {
    return http.delete(`/api/blog/tags/${id}`)
  },
}
