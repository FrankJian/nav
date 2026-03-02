import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

const TOKEN_KEY = 'navigate_token'
const USER_KEY = 'navigate_user'

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(TOKEN_KEY) || ''
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(USER_KEY)
      // 刷新当前页，让首页等正常显示并展示登录按钮，不强制跳转登录页
      window.location.reload()
    }
    return Promise.reject(error)
  }
)

export default api
