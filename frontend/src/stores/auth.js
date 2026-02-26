import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)

  const isAuthenticated = computed(() => !!token.value)

  // 设置 token
  function setToken(newToken) {
    token.value = newToken
    if (newToken) {
      localStorage.setItem('token', newToken)
      api.defaults.headers.common['Authorization'] = `Bearer ${newToken}`
    } else {
      localStorage.removeItem('token')
      delete api.defaults.headers.common['Authorization']
    }
  }

  // 设置用户信息
  function setUser(userData) {
    user.value = userData
  }

  // 登录
  async function login(email, password) {
    try {
      const response = await api.post('/auth/login', { email, password })
      setToken(response.data.access_token)
      await fetchUser()
      return { success: true }
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || '登录失败'
      }
    }
  }

  // 注册
  async function register(display_name, email, password) {
    try {
      await api.post('/auth/register', { display_name, email, password })
      return { success: true }
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || '注册失败'
      }
    }
  }

  // 获取用户信息
  async function fetchUser() {
    try {
      const response = await api.get('/auth/me')
      setUser(response.data)
    } catch (error) {
      console.error('获取用户信息失败:', error)
      logout()
    }
  }

  // 登出
  function logout() {
    setToken('')
    setUser(null)
  }

  // 初始化：如果有 token，设置到 axios 并获取用户信息
  if (token.value) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
    fetchUser()
  }

  return {
    token,
    user,
    isAuthenticated,
    login,
    register,
    logout,
    fetchUser
  }
})
