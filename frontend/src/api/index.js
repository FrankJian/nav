import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器：优先从 Cookie 取 token（与 auth store 一致，移动端 Cookie 更持久）
function getToken() {
  const match = document.cookie.match(/(^| )navigate_token=([^;]+)/)
  if (match) return decodeURIComponent(match[2]).trim()
  return localStorage.getItem('token') || ''
}

api.interceptors.request.use(
  (config) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('navigate_user')
      document.cookie = 'navigate_token=; path=/; max-age=0'
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
