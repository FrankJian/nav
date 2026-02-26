<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-500 to-primary-700 dark:from-gray-800 dark:to-gray-900">
    <div class="card p-8 w-full max-w-md">
      <h1 class="text-3xl font-bold text-center mb-6 text-primary-600 dark:text-primary-400">
        注册账号
      </h1>
      <form @submit.prevent="handleRegister" class="space-y-4">
        <div>
          <label class="block text-sm font-medium mb-2">显示名</label>
          <input
            v-model="displayName"
            type="text"
            required
            class="input"
            placeholder="请输入显示名（用于页面显示）"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">邮箱</label>
          <input
            v-model="email"
            type="email"
            required
            class="input"
            placeholder="请输入邮箱（用于登录）"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">密码</label>
          <input
            v-model="password"
            type="password"
            required
            class="input"
            placeholder="请输入密码"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">确认密码</label>
          <input
            v-model="confirmPassword"
            type="password"
            required
            class="input"
            placeholder="请再次输入密码"
          />
        </div>
        <div v-if="error" class="text-red-500 text-sm">{{ error }}</div>
        <button type="submit" class="btn-primary w-full" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
        <div class="text-center text-sm">
          <span class="text-gray-600 dark:text-gray-400">已有账号？</span>
          <router-link to="/login" class="text-primary-600 hover:text-primary-700 dark:text-primary-400">
            立即登录
          </router-link>
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

const displayName = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const error = ref('')
const loading = ref(false)

const handleRegister = async () => {
  error.value = ''
  
  if (password.value !== confirmPassword.value) {
    error.value = '两次输入的密码不一致'
    return
  }
  
  if (password.value.length < 6) {
    error.value = '密码长度至少为6位'
    return
  }
  
  loading.value = true
  
  const result = await authStore.register(displayName.value, email.value, password.value)
  
  if (result.success) {
    router.push('/login')
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
