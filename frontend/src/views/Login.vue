<template>
  <div class="auth-container">
    <div class="auth-card glass">
      <h1 class="auth-title gradient-text">网站导航管理系统</h1>
      <form @submit.prevent="handleLogin" class="auth-form">
        <div class="form-group">
          <label>邮箱</label>
          <input
            v-model="email"
            type="email"
            required
            class="input"
            placeholder="请输入邮箱"
          />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input
            v-model="password"
            type="password"
            required
            class="input"
            placeholder="请输入密码"
          />
        </div>
        <div v-if="error" class="form-error">{{ error }}</div>
        <button type="submit" class="btn-primary w-full" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
        <div class="auth-footer">
          <span>还没有账号？</span>
          <router-link to="/register" class="auth-link">立即注册</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const handleLogin = async () => {
  error.value = ''
  loading.value = true
  
  const result = await authStore.login(email.value, password.value)
  
  if (result.success) {
    router.push('/')
  } else {
    error.value = result.message
  }
  
  loading.value = false
}
</script>

<style scoped>
.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1rem;
}

.dark .auth-container {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}

.auth-card {
  width: 100%;
  max-width: 28rem;
  padding: 2rem;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
}

.auth-title {
  font-size: 1.875rem;
  font-weight: 700;
  text-align: center;
  margin-bottom: 1.5rem;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text);
}

.form-error {
  color: #ef4444;
  font-size: 0.875rem;
}

.w-full {
  width: 100%;
}

.auth-footer {
  text-align: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
}

.auth-link {
  color: var(--primary);
  text-decoration: none;
  font-weight: 500;
  margin-left: 0.25rem;
  transition: var(--transition);
}

.auth-link:hover {
  color: var(--primary-hover);
  text-decoration: underline;
}
</style>
