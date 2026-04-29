import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = ref(localStorage.getItem('admin_token') || null)
  const admin = ref(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value)

  // Actions
  async function login(username, password) {
    try {
      const response = await authAPI.login(username, password)
      token.value = response.data.access_token
      admin.value = {
        id: response.data.admin_id,
        username: response.data.username
      }

      // Save to localStorage
      localStorage.setItem('admin_token', token.value)

      return true
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  }

  function logout() {
    token.value = null
    admin.value = null
    localStorage.removeItem('admin_token')
  }

  async function loadAdminInfo() {
    if (!token.value) return

    try {
      const response = await authAPI.getMe()
      admin.value = response.data
    } catch (error) {
      console.error('Failed to load admin info:', error)
      logout()
    }
  }

  return {
    token,
    admin,
    isAuthenticated,
    login,
    logout,
    loadAdminInfo
  }
})
