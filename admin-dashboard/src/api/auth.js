import apiClient from './client'

export const authAPI = {
  login(username, password) {
    return apiClient.post('/admin/auth/login', { username, password })
  },

  getMe() {
    return apiClient.get('/admin/auth/me')
  },

  verifyToken() {
    return apiClient.post('/admin/auth/verify')
  }
}
