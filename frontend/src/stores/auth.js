import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'

const USER_STORAGE_KEY = 'navigate_user'

function getStoredUser() {
  try {
    const raw = localStorage.getItem(USER_STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(getStoredUser())

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

  // 设置用户信息（同时写入 localStorage，便于关闭浏览器后恢复）
  function setUser(userData) {
    user.value = userData
    if (userData) {
      localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(userData))
    } else {
      localStorage.removeItem(USER_STORAGE_KEY)
    }
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

  // 获取用户信息（仅 401 时清除登录状态，避免网络波动导致被踢出）
  async function fetchUser() {
    try {
      const response = await api.get('/auth/me')
      setUser(response.data)
    } catch (error) {
      console.error('获取用户信息失败:', error)
      if (error.response?.status === 401) {
        logout()
      }
      // 非 401（如网络错误）不清除 token，保留本地登录状态
    }
  }

  // 登出（同时清除本地缓存）
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
