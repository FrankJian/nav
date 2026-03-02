import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'

const USER_KEY = 'navigate_user'
const TOKEN_KEY = 'navigate_token'

function getStoredToken() {
  try {
    return localStorage.getItem(TOKEN_KEY) || ''
  } catch {
    return ''
  }
}

function getStoredUser() {
  try {
    const raw = localStorage.getItem(USER_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(getStoredToken())
  const user = ref(getStoredUser())

  const isAuthenticated = computed(() => !!token.value)

  function setToken(newToken) {
    token.value = newToken
    if (newToken) {
      localStorage.setItem(TOKEN_KEY, newToken)
      api.defaults.headers.common['Authorization'] = `Bearer ${newToken}`
    } else {
      localStorage.removeItem(TOKEN_KEY)
      delete api.defaults.headers.common['Authorization']
    }
  }

  function setUser(userData) {
    user.value = userData
    if (userData) {
      localStorage.setItem(USER_KEY, JSON.stringify(userData))
    } else {
      localStorage.removeItem(USER_KEY)
    }
  }

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

  async function fetchUser() {
    try {
      const response = await api.get('/auth/me')
      setUser(response.data)
    } catch (error) {
      if (error.response?.status === 401) {
        logout()
      }
    }
  }

  function logout() {
    setToken('')
    setUser(null)
  }

  // 应用启动时：有 token 则设置请求头并拉取用户信息
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
