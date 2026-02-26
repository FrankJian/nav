<template>
  <div class="app-container">
    <!-- 顶部导航栏 -->
    <nav class="navbar">
      <div class="navbar-container">
        <!-- 左侧：Logo 和搜索 -->
        <div class="navbar-left">
          <div class="logo-section">
            <div class="logo-icon">
              <Icon icon="mdi:compass-outline" />
            </div>
            <h1 class="logo-text">网站导航</h1>
          </div>
          
          <!-- 搜索栏整合到导航栏 -->
          <div class="navbar-search">
            <Icon icon="mdi:magnify" class="search-icon" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索网站、分类..."
              class="search-input"
            />
          </div>
        </div>

        <!-- 右侧：操作按钮和用户信息 -->
        <div class="navbar-right">
          <!-- 操作按钮组 -->
          <div class="action-buttons">
            <button
              @click="showAddCategoryModal = true"
              class="action-btn"
              title="添加分类"
            >
              <Icon icon="mdi:folder-plus-outline" />
              <span class="action-label">分类</span>
            </button>
            <button
              @click="showAddWebsiteModal = true"
              class="action-btn action-btn-primary"
              title="添加网站"
            >
              <Icon icon="mdi:plus" />
              <span class="action-label">添加</span>
            </button>
            <button
              @click="toggleDarkMode"
              class="action-btn"
              :title="isDark ? '切换到浅色模式' : '切换到深色模式'"
            >
              <Icon :icon="isDark ? 'mdi:weather-sunny' : 'mdi:weather-night'" />
            </button>
          </div>

          <!-- 用户菜单 -->
          <div class="user-menu" ref="userMenuRef">
            <div 
              @click.stop="toggleUserDropdown"
              class="user-profile"
              title="用户菜单"
            >
              <div class="user-avatar">
                {{ userInitial }}
              </div>
              <div class="user-info-text hidden-sm">
                <div class="user-name">{{ authStore.user?.display_name || '用户' }}</div>
                <div class="user-email">{{ authStore.user?.email || '' }}</div>
              </div>
              <Icon 
                icon="mdi:chevron-down" 
                class="user-chevron hidden-sm"
                :class="{ 'chevron-rotate': showUserDropdown }"
              />
            </div>
            
            <!-- 下拉菜单 -->
            <div 
              v-if="showUserDropdown"
              class="user-dropdown glass"
            >
              <button
                @click="handleEditUserInfo"
                class="dropdown-item"
              >
                <Icon icon="mdi:account-edit" />
                <span>修改用户信息</span>
              </button>
              <div class="dropdown-divider"></div>
              <button
                @click="handleLogoutClick"
                class="dropdown-item dropdown-item-danger"
              >
                <Icon icon="mdi:logout" />
                <span>退出登录</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- 内容区域 -->
    <div class="content-section">

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <!-- 空状态 -->
      <div v-else-if="filteredCategories.length === 0" class="empty-state">
        <div class="empty-content glass">
          <Icon icon="mdi:web-off" class="empty-icon" />
          <p>暂无网站</p>
          <button @click="showAddCategoryModal = true" class="btn-primary">
            创建第一个分类
          </button>
        </div>
      </div>

      <!-- 分类和网站展示 -->
      <div v-else class="content-area">
        <!-- 分类指示器 -->
        <div class="category-indicators">
          <!-- 常用分类按钮 -->
          <button
            @click="showFavorites = true"
            class="category-btn"
            :class="{ active: showFavorites }"
          >
            <Icon icon="mdi:star" />
            <span>常用</span>
          </button>
          
          <!-- 其他分类按钮 -->
          <div
            v-for="(category, index) in filteredCategories"
            :key="category.id"
            class="category-btn-wrapper"
          >
            <button
              @click="selectCategory(category, index)"
              class="category-btn"
              :class="{ active: !showFavorites && currentCategoryIndex === index }"
            >
              <span>{{ category.name }}</span>
            </button>
            <button
              @click.stop="editCategory(category)"
              class="category-edit-btn"
              title="编辑分类"
            >
              <Icon icon="mdi:pencil" />
            </button>
          </div>
        </div>

        <!-- 轮播容器 -->
        <div
          class="carousel-container"
          @wheel="handleWheel"
          ref="carouselContainer"
        >
          <!-- 常用分类 -->
          <div
            v-if="showFavorites"
            class="carousel-slide"
          >
            <div class="website-grid">
              <div
                v-for="website in favoriteWebsites"
                :key="website.id"
                class="website-card-wrapper"
              >
                <div
                  @click="handleWebsiteClick(website)"
                  class="website-card glass-strong"
                >
                  <div class="website-content">
                    <!-- 图标 -->
                    <div class="website-icon-wrapper">
                      <div class="website-icon-bg">
                        <img
                          v-if="website.icon && (website.icon.startsWith('http://') || website.icon.startsWith('https://'))"
                          :src="website.icon"
                          :alt="website.title"
                          class="website-icon-img"
                          @error="handleImageError"
                        />
                        <Icon
                          v-else-if="website.icon"
                          :icon="website.icon"
                          class="website-icon-svg"
                        />
                        <span v-else class="website-icon-text">
                          {{ website.title.charAt(0).toUpperCase() }}
                        </span>
                      </div>
                    </div>
                    
                    <!-- 标题 -->
                    <h3 class="website-title">{{ website.title }}</h3>
                    
                    <!-- 描述 -->
                    <p
                      v-if="website.description"
                      class="website-description"
                    >
                      {{ website.description }}
                    </p>
                    <div v-else class="website-description-placeholder"></div>
                    
                    <!-- 点击次数 -->
                    <div class="website-stats">
                      <Icon icon="mdi:mouse-click" />
                      <span>{{ website.click_count }}</span>
                    </div>
                  </div>
                </div>

                <!-- 编辑按钮 -->
                <button
                  @click.stop="toggleFavorite(website)"
                  class="website-action-btn favorite-btn"
                  title="取消常用"
                >
                  <Icon icon="mdi:star" />
                </button>
                <button
                  @click.stop="editWebsite(website)"
                  class="website-action-btn edit-btn"
                  title="编辑网站"
                >
                  <Icon icon="mdi:pencil" />
                </button>
              </div>
            </div>
            <div v-if="favoriteWebsites.length === 0" class="empty-favorites">
              <Icon icon="mdi:star-outline" class="empty-icon" />
              <p>还没有常用网站，点击网站卡片上的星标按钮添加</p>
            </div>
          </div>

          <!-- 其他分类 -->
          <div
            v-else
            class="carousel-track"
            :style="{ transform: `translateX(-${currentCategoryIndex * 100}%)` }"
          >
            <div
              v-for="category in filteredCategories"
              :key="category.id"
              class="carousel-slide"
            >
              <div class="website-grid">
                <div
                  v-for="website in getWebsitesByCategory(category.id)"
                  :key="website.id"
                  class="website-card-wrapper"
                >
                  <div
                    @click="handleWebsiteClick(website)"
                    class="website-card glass-strong"
                  >
                    <div class="website-content">
                      <!-- 图标 -->
                      <div class="website-icon-wrapper">
                        <div class="website-icon-bg">
                          <img
                            v-if="website.icon && (website.icon.startsWith('http://') || website.icon.startsWith('https://'))"
                            :src="website.icon"
                            :alt="website.title"
                            class="website-icon-img"
                            @error="handleImageError"
                          />
                          <Icon
                            v-else-if="website.icon"
                            :icon="website.icon"
                            class="website-icon-svg"
                          />
                          <span v-else class="website-icon-text">
                            {{ website.title.charAt(0).toUpperCase() }}
                          </span>
                        </div>
                      </div>
                      
                      <!-- 标题 -->
                      <h3 class="website-title">{{ website.title }}</h3>
                      
                      <!-- 描述 -->
                      <p
                        v-if="website.description"
                        class="website-description"
                      >
                        {{ website.description }}
                      </p>
                      <div v-else class="website-description-placeholder"></div>
                      
                      <!-- 点击次数 -->
                      <div class="website-stats">
                        <Icon icon="mdi:mouse-click" />
                        <span>{{ website.click_count }}</span>
                      </div>
                    </div>
                  </div>

                  <!-- 常用按钮和编辑按钮 -->
                  <button
                    @click.stop="toggleFavorite(website)"
                    class="website-action-btn favorite-btn"
                    :title="website.is_favorite ? '取消常用' : '设为常用'"
                  >
                    <Icon 
                      :icon="website.is_favorite ? 'mdi:star' : 'mdi:star-outline'"
                      :class="{ 'star-filled': website.is_favorite }"
                    />
                  </button>
                  <button
                    @click.stop="editWebsite(website)"
                    class="website-action-btn edit-btn"
                    title="编辑网站"
                  >
                    <Icon icon="mdi:pencil" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 左右导航箭头 -->
        <div v-if="!showFavorites && filteredCategories.length > 1" class="carousel-nav">
          <button
            @click="previousCategory"
            :disabled="currentCategoryIndex === 0"
            class="carousel-nav-btn"
            title="上一个分类"
          >
            <Icon icon="mdi:chevron-left" />
          </button>
          <div class="carousel-counter">
            {{ currentCategoryIndex + 1 }} / {{ filteredCategories.length }}
          </div>
          <button
            @click="nextCategory"
            :disabled="currentCategoryIndex === filteredCategories.length - 1"
            class="carousel-nav-btn"
            title="下一个分类"
          >
            <Icon icon="mdi:chevron-right" />
          </button>
        </div>
      </div>
    </div>

    <!-- 添加/编辑分类模态框 -->
    <div
      v-if="showAddCategoryModal || editingCategory"
      class="modal-overlay"
      @click.self="closeCategoryModal"
    >
      <div class="modal glass">
        <h3 class="modal-title">
          {{ editingCategory ? '编辑分类' : '添加分类' }}
        </h3>
        <form @submit.prevent="saveCategory" class="modal-form">
          <div class="form-group">
            <label>分类名称</label>
            <input v-model="categoryForm.name" type="text" required class="input" />
          </div>
          <div class="form-actions">
            <button type="submit" class="btn-primary flex-1">保存</button>
            <button type="button" @click="closeCategoryModal" class="btn-secondary flex-1">取消</button>
            <button
              v-if="editingCategory"
              type="button"
              @click="deleteCategory(editingCategory.id)"
              class="btn-secondary btn-danger"
            >
              删除
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 用户信息编辑模态框 -->
    <div
      v-if="showUserModal"
      class="modal-overlay"
      @click.self="closeUserModal"
    >
      <div class="modal glass">
        <h3 class="modal-title">个人信息</h3>
        <form @submit.prevent="saveUserInfo" class="modal-form">
          <div class="form-group">
            <label>显示名</label>
            <input
              v-model="userForm.display_name"
              type="text"
              required
              class="input"
              placeholder="请输入显示名"
            />
          </div>
          <div class="form-group">
            <label>邮箱</label>
            <input
              v-model="userForm.email"
              type="email"
              required
              class="input"
              placeholder="请输入邮箱（用于登录）"
            />
            <p class="form-hint">
              邮箱用于登录，修改后需要使用新邮箱登录
            </p>
          </div>
          <div v-if="userFormError" class="form-error">{{ userFormError }}</div>
          <div class="form-actions">
            <button type="submit" class="btn-primary flex-1" :disabled="savingUserInfo">
              {{ savingUserInfo ? '保存中...' : '保存' }}
            </button>
            <button type="button" @click="closeUserModal" class="btn-secondary flex-1">取消</button>
          </div>
        </form>
        <div class="modal-divider"></div>
        <h4 class="modal-subtitle">修改密码</h4>
        <form @submit.prevent="changePassword" class="modal-form">
          <div class="form-group">
            <label>当前密码</label>
            <input
              v-model="passwordForm.current_password"
              type="password"
              class="input"
              placeholder="请输入当前密码"
              autocomplete="current-password"
            />
          </div>
          <div class="form-group">
            <label>新密码</label>
            <input
              v-model="passwordForm.new_password"
              type="password"
              class="input"
              placeholder="至少 6 位"
              autocomplete="new-password"
            />
          </div>
          <div class="form-group">
            <label>确认新密码</label>
            <input
              v-model="passwordForm.confirm_password"
              type="password"
              class="input"
              placeholder="再次输入新密码"
              autocomplete="new-password"
            />
          </div>
          <div v-if="passwordFormError" class="form-error">{{ passwordFormError }}</div>
          <div class="form-actions">
            <button type="submit" class="btn-primary flex-1" :disabled="savingPassword">
              {{ savingPassword ? '修改中...' : '修改密码' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 添加/编辑网站模态框 -->
    <div
      v-if="showAddWebsiteModal || editingWebsite"
      class="modal-overlay"
      @click.self="closeWebsiteModal"
    >
      <div class="modal glass modal-large">
        <h3 class="modal-title">
          {{ editingWebsite ? '编辑网站' : '添加网站' }}
        </h3>
        <form @submit.prevent="saveWebsite" class="modal-form">
          <div class="form-group">
            <label>网址</label>
            <div class="input-group">
              <input
                v-model="websiteForm.url"
                type="url"
                required
                class="input"
                placeholder="输入网址，然后点击自动获取"
                @blur="handleUrlBlur"
              />
              <button
                type="button"
                @click="scrapeWebsiteInfo"
                :disabled="!websiteForm.url || scraping"
                class="btn-secondary"
              >
                {{ scraping ? '获取中...' : '自动获取' }}
              </button>
            </div>
          </div>
          <div class="form-group">
            <label>网站标题</label>
            <input v-model="websiteForm.title" type="text" required class="input" />
          </div>
          <div class="form-group">
            <label>分类</label>
            <select v-model="websiteForm.category_id" required class="input">
              <option value="">请选择分类</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                {{ cat.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>图标</label>
            <input
              v-model="websiteForm.icon"
              type="text"
              class="input"
              placeholder="Iconify格式 (如: mdi:github) 或图标URL"
            />
            <p class="form-hint">
              系统会自动从网站抓取图标，也可以手动输入 Iconify 图标名称或图标URL
            </p>
          </div>
          <div class="form-group">
            <label>描述</label>
            <textarea v-model="websiteForm.description" class="input" rows="3"></textarea>
          </div>
          <div class="form-actions">
            <button type="submit" class="btn-primary flex-1">保存</button>
            <button type="button" @click="closeWebsiteModal" class="btn-secondary flex-1">取消</button>
            <button
              v-if="editingWebsite"
              type="button"
              @click="deleteWebsite(editingWebsite.id)"
              class="btn-secondary btn-danger"
            >
              删除
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const router = useRouter()
const authStore = useAuthStore()

const categories = ref([])
const websites = ref([])
const searchQuery = ref('')
const loading = ref(true)
const isDark = ref(localStorage.getItem('darkMode') === 'true')
const showAddCategoryModal = ref(false)
const showAddWebsiteModal = ref(false)
const editingCategory = ref(null)
const editingWebsite = ref(null)
const scraping = ref(false)
const urlBlurTimeout = ref(null)
const currentCategoryIndex = ref(0)
const carouselContainer = ref(null)
const wheelTimeout = ref(null)
const showFavorites = ref(false)
const showUserModal = ref(false)
const showUserDropdown = ref(false)
const savingUserInfo = ref(false)
const userFormError = ref('')
const userMenuRef = ref(null)

const userForm = ref({
  display_name: '',
  email: ''
})

const passwordForm = ref({
  current_password: '',
  new_password: '',
  confirm_password: ''
})
const passwordFormError = ref('')
const savingPassword = ref(false)

const categoryForm = ref({
  name: ''
})

const websiteForm = ref({
  title: '',
  url: '',
  category_id: '',
  icon: '',
  description: ''
})

// 初始化暗色模式
if (isDark.value) {
  document.documentElement.classList.add('dark')
}

const toggleDarkMode = () => {
  isDark.value = !isDark.value
  if (isDark.value) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('darkMode', 'true')
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('darkMode', 'false')
  }
}

const fetchData = async () => {
  try {
    loading.value = true
    const [categoriesRes, websitesRes] = await Promise.all([
      api.get('/categories'),
      api.get('/websites')
    ])
    categories.value = categoriesRes.data
    websites.value = websitesRes.data
    currentCategoryIndex.value = 0
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
  }
}

const getWebsitesByCategory = (categoryId) => {
  let categoryWebsites = websites.value.filter(w => w.category_id === categoryId)
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    categoryWebsites = categoryWebsites.filter(w =>
      w.title.toLowerCase().includes(query) ||
      w.url.toLowerCase().includes(query) ||
      (w.description && w.description.toLowerCase().includes(query))
    )
  }
  
  return categoryWebsites.sort((a, b) => a.sort_order - b.sort_order)
}

const favoriteWebsites = computed(() => {
  let favorites = websites.value.filter(w => w.is_favorite === 1)
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    favorites = favorites.filter(w =>
      w.title.toLowerCase().includes(query) ||
      w.url.toLowerCase().includes(query) ||
      (w.description && w.description.toLowerCase().includes(query))
    )
  }
  
  return favorites.sort((a, b) => b.click_count - a.click_count)
})

const selectCategory = (category, index) => {
  showFavorites.value = false
  currentCategoryIndex.value = index
}

const toggleFavorite = async (website) => {
  try {
    const response = await api.post(`/websites/${website.id}/toggle-favorite`)
    website.is_favorite = response.data.is_favorite
    if (showFavorites.value && website.is_favorite === 0) {
      await fetchData()
    }
  } catch (error) {
    console.error('切换常用状态失败:', error)
    alert(error.response?.data?.detail || '操作失败')
  }
}

const handleWebsiteClick = async (website) => {
  try {
    await api.post(`/websites/${website.id}/click`)
    window.open(website.url, '_blank')
    website.click_count += 1
  } catch (error) {
    console.error('记录点击失败:', error)
    window.open(website.url, '_blank')
  }
}

const editCategory = (category) => {
  editingCategory.value = category
  categoryForm.value = {
    name: category.name
  }
  showAddCategoryModal.value = true
}

const editWebsite = (website) => {
  editingWebsite.value = website
  websiteForm.value = {
    title: website.title,
    url: website.url,
    category_id: website.category_id,
    icon: website.icon || '',
    description: website.description || ''
  }
  showAddWebsiteModal.value = true
}

const saveCategory = async () => {
  try {
    if (editingCategory.value) {
      await api.put(`/categories/${editingCategory.value.id}`, categoryForm.value)
    } else {
      await api.post('/categories', categoryForm.value)
    }
    closeCategoryModal()
    fetchData()
  } catch (error) {
    console.error('保存分类失败:', error)
    alert(error.response?.data?.detail || '保存失败')
  }
}

const saveWebsite = async () => {
  try {
    if (editingWebsite.value) {
      await api.put(`/websites/${editingWebsite.value.id}`, websiteForm.value)
    } else {
      await api.post('/websites', websiteForm.value)
    }
    closeWebsiteModal()
    fetchData()
  } catch (error) {
    console.error('保存网站失败:', error)
    alert(error.response?.data?.detail || '保存失败')
  }
}

const deleteCategory = async (id) => {
  if (!confirm('确定要删除这个分类吗？分类下的所有网站也会被删除。')) {
    return
  }
  try {
    await api.delete(`/categories/${id}`)
    closeCategoryModal()
    fetchData()
  } catch (error) {
    console.error('删除分类失败:', error)
    alert(error.response?.data?.detail || '删除失败')
  }
}

const deleteWebsite = async (id) => {
  if (!confirm('确定要删除这个网站吗？')) {
    return
  }
  try {
    await api.delete(`/websites/${id}`)
    closeWebsiteModal()
    fetchData()
  } catch (error) {
    console.error('删除网站失败:', error)
    alert(error.response?.data?.detail || '删除失败')
  }
}

const scrapeWebsiteInfo = async () => {
  if (!websiteForm.value.url) {
    return
  }
  
  scraping.value = true
  try {
    const response = await api.get('/websites/scrape', {
      params: { url: websiteForm.value.url }
    })
    
    const info = response.data
    
    if (info.title && !websiteForm.value.title) {
      websiteForm.value.title = info.title
    }
    if (info.icon && !websiteForm.value.icon) {
      websiteForm.value.icon = info.icon
    }
    if (info.description && !websiteForm.value.description) {
      websiteForm.value.description = info.description
    }
    
    if (!websiteForm.value.title && websiteForm.value.url) {
      try {
        const urlObj = new URL(websiteForm.value.url.startsWith('http') ? websiteForm.value.url : `https://${websiteForm.value.url}`)
        websiteForm.value.title = urlObj.hostname.replace('www.', '')
      } catch (e) {
        websiteForm.value.title = '未命名网站'
      }
    }
  } catch (error) {
    console.error('抓取网站信息失败:', error)
    if (!websiteForm.value.title && websiteForm.value.url) {
      try {
        const urlObj = new URL(websiteForm.value.url.startsWith('http') ? websiteForm.value.url : `https://${websiteForm.value.url}`)
        websiteForm.value.title = urlObj.hostname.replace('www.', '')
      } catch (e) {
        websiteForm.value.title = '未命名网站'
      }
    }
  } finally {
    scraping.value = false
  }
}

const handleUrlBlur = () => {
  urlBlurTimeout.value = setTimeout(() => {
    if (websiteForm.value.url && !websiteForm.value.title && !editingWebsite.value) {
      scrapeWebsiteInfo()
    }
  }, 300)
}

const closeCategoryModal = () => {
  showAddCategoryModal.value = false
  editingCategory.value = null
  categoryForm.value = {
    name: ''
  }
}

const closeWebsiteModal = () => {
  showAddWebsiteModal.value = false
  editingWebsite.value = null
  scraping.value = false
  if (urlBlurTimeout.value) {
    clearTimeout(urlBlurTimeout.value)
    urlBlurTimeout.value = null
  }
  websiteForm.value = {
    title: '',
    url: '',
    category_id: '',
    icon: '',
    description: ''
  }
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

const handleImageError = (event) => {
  event.target.style.display = 'none'
}

const userInitial = computed(() => {
  if (authStore.user?.display_name) {
    return authStore.user.display_name.charAt(0).toUpperCase()
  }
  if (authStore.user?.email) {
    return authStore.user.email.charAt(0).toUpperCase()
  }
  return 'U'
})

const nextCategory = () => {
  if (currentCategoryIndex.value < filteredCategories.value.length - 1) {
    currentCategoryIndex.value++
  }
}

const previousCategory = () => {
  if (currentCategoryIndex.value > 0) {
    currentCategoryIndex.value--
  }
}

const handleWheel = (event) => {
  if (showFavorites.value) {
    return
  }
  
  event.preventDefault()
  
  if (wheelTimeout.value) {
    return
  }
  
  wheelTimeout.value = setTimeout(() => {
    wheelTimeout.value = null
  }, 300)
  
  if (event.deltaY > 0) {
    nextCategory()
  } else if (event.deltaY < 0) {
    previousCategory()
  }
}

const filteredCategories = computed(() => {
  if (!searchQuery.value) {
    return categories.value
  }
  
  const query = searchQuery.value.toLowerCase()
  const filteredWebsites = websites.value.filter(w =>
    w.title.toLowerCase().includes(query) ||
    w.url.toLowerCase().includes(query) ||
    (w.description && w.description.toLowerCase().includes(query))
  )
  
  const categoryIds = new Set(filteredWebsites.map(w => w.category_id))
  const filtered = categories.value.filter(c => categoryIds.has(c.id))
  
  if (currentCategoryIndex.value >= filtered.length) {
    currentCategoryIndex.value = 0
  }
  
  return filtered
})

const saveUserInfo = async () => {
  userFormError.value = ''
  savingUserInfo.value = true
  
  try {
    await api.put('/auth/me', userForm.value)
    await authStore.fetchUser()
    closeUserModal()
  } catch (error) {
    console.error('更新用户信息失败:', error)
    userFormError.value = error.response?.data?.detail || '更新失败'
  } finally {
    savingUserInfo.value = false
  }
}

const changePassword = async () => {
  passwordFormError.value = ''
  if (passwordForm.value.new_password.length < 6) {
    passwordFormError.value = '新密码长度至少为 6 位'
    return
  }
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    passwordFormError.value = '两次输入的新密码不一致'
    return
  }
  savingPassword.value = true
  try {
    await api.put('/auth/me/password', {
      current_password: passwordForm.value.current_password,
      new_password: passwordForm.value.new_password
    })
    closeUserModal()
    authStore.logout()
    router.push('/login')
  } catch (error) {
    passwordFormError.value = error.response?.data?.detail || '修改失败'
  } finally {
    savingPassword.value = false
  }
}

const closeUserModal = () => {
  showUserModal.value = false
  userFormError.value = ''
  passwordFormError.value = ''
  passwordForm.value = { current_password: '', new_password: '', confirm_password: '' }
  if (authStore.user) {
    userForm.value = {
      display_name: authStore.user.display_name,
      email: authStore.user.email
    }
  }
}

const toggleUserDropdown = (event) => {
  event.stopPropagation()
  showUserDropdown.value = !showUserDropdown.value
}

const handleEditUserInfo = (event) => {
  event.stopPropagation()
  if (authStore.user) {
    userForm.value = {
      display_name: authStore.user.display_name,
      email: authStore.user.email
    }
  }
  showUserModal.value = true
  showUserDropdown.value = false
}

const handleLogoutClick = (event) => {
  event.stopPropagation()
  handleLogout()
  showUserDropdown.value = false
}

const openUserModal = () => {
  if (authStore.user) {
    userForm.value = {
      display_name: authStore.user.display_name,
      email: authStore.user.email
    }
  }
  showUserModal.value = true
}

watch(() => showUserModal.value, (newVal) => {
  if (newVal && authStore.user) {
    userForm.value = {
      display_name: authStore.user.display_name,
      email: authStore.user.email
    }
  }
})

// 点击外部关闭下拉菜单
const handleClickOutside = (event) => {
  if (userMenuRef.value && !userMenuRef.value.contains(event.target)) {
    showUserDropdown.value = false
  }
}

onMounted(() => {
  fetchData()
  if (authStore.isAuthenticated && !authStore.user) {
    authStore.fetchUser()
  }
  // 添加点击外部关闭下拉菜单的监听
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  // 移除事件监听
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  background-attachment: fixed;
  position: relative;
  overflow-x: hidden;
}

.app-container::before {
  content: '';
  position: fixed;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
  animation: float 20s ease-in-out infinite;
  pointer-events: none;
  z-index: 0;
}

.app-container::after {
  content: '';
  position: fixed;
  top: 50%;
  right: -30%;
  width: 80%;
  height: 80%;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.2) 0%, transparent 70%);
  animation: float 15s ease-in-out infinite reverse;
  pointer-events: none;
  z-index: 0;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) rotate(0deg);
  }
  33% {
    transform: translate(30px, -30px) rotate(120deg);
  }
  66% {
    transform: translate(-20px, 20px) rotate(240deg);
  }
}

.dark .app-container {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #312e81 100%);
}

.dark .app-container::before {
  background: radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, transparent 70%);
}

.dark .app-container::after {
  background: radial-gradient(circle, rgba(139, 92, 246, 0.1) 0%, transparent 70%);
}

/* 导航栏 - 现代化设计 */
.navbar {
  position: sticky;
  top: 0;
  z-index: 50;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(24px) saturate(200%);
  -webkit-backdrop-filter: blur(24px) saturate(200%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
  transition: var(--transition);
}

.dark .navbar {
  background: rgba(15, 23, 42, 0.3);
  border-bottom-color: rgba(255, 255, 255, 0.15);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
}

.navbar-container {
  width: 100%;
  max-width: 100%;
  padding: 0 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 72px;
  gap: 2rem;
  position: relative;
  z-index: 1;
}

/* 左侧：Logo 和搜索 */
.navbar-left {
  display: flex;
  align-items: center;
  gap: 2rem;
  flex: 1;
  min-width: 0;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-shrink: 0;
}

.logo-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--primary) 0%, #8b5cf6 100%);
  color: white;
  font-size: 1.25rem;
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.3);
  transition: var(--transition);
}

.logo-icon:hover {
  transform: scale(1.05) rotate(5deg);
  box-shadow: 0 12px 32px rgba(99, 102, 241, 0.5);
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--primary) 0%, #8b5cf6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  white-space: nowrap;
}

/* 导航栏内搜索 */
.navbar-search {
  position: relative;
  flex: 1;
  max-width: 500px;
  min-width: 200px;
}

.navbar-search .search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  color: var(--text-tertiary);
  pointer-events: none;
  z-index: 1;
}

.navbar-search .search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.75rem;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.3);
  font-size: 0.875rem;
  transition: all 0.3s ease;
  color: var(--text);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.navbar-search .search-input::placeholder {
  color: rgba(255, 255, 255, 0.7);
}

.navbar-search .search-input:focus {
  background: rgba(255, 255, 255, 0.35);
  border-color: rgba(255, 255, 255, 0.5);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2), 0 8px 24px rgba(0, 0, 0, 0.15);
  outline: none;
  transform: translateY(-1px);
}

.dark .navbar-search .search-input {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
  color: var(--text);
}

.dark .navbar-search .search-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.dark .navbar-search .search-input:focus {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
}

/* 右侧：操作按钮和用户 */
.navbar-right {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-shrink: 0;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: var(--radius-sm);
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition-hover);
  white-space: nowrap;
}

.action-btn:hover {
  background: rgba(0, 0, 0, 0.05);
  color: var(--text);
  transform: translateY(-1px);
}

.action-btn:active {
  transform: translateY(0);
}

.dark .action-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.action-btn-primary {
  background: linear-gradient(135deg, var(--primary) 0%, #8b5cf6 100%);
  color: white;
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.action-btn-primary:hover {
  background: linear-gradient(135deg, var(--primary-hover) 0%, #7c3aed 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.5);
}

.action-btn-primary:active {
  transform: translateY(0);
}

.action-label {
  font-size: 0.875rem;
}

/* 用户菜单 */
.user-menu {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding-left: 1rem;
  border-left: 1px solid var(--border);
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.375rem 0.75rem;
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: var(--transition);
}

.user-profile:hover {
  background: rgba(0, 0, 0, 0.04);
}

.dark .user-profile:hover {
  background: rgba(255, 255, 255, 0.08);
}

.user-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary) 0%, #8b5cf6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 0.875rem;
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.4), 0 0 0 2px rgba(255, 255, 255, 0.3);
  flex-shrink: 0;
  transition: var(--transition);
}

.user-profile:hover .user-avatar {
  transform: scale(1.1);
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.5);
}

.user-info-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.user-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-email {
  font-size: 0.75rem;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-chevron {
  width: 16px;
  height: 16px;
  color: var(--text-tertiary);
  transition: var(--transition);
}

.user-profile:hover .user-chevron {
  color: var(--text);
}

.chevron-rotate {
  transform: rotate(180deg);
}

/* 用户下拉菜单 */
.user-dropdown {
  position: absolute;
  top: calc(100% + 0.75rem);
  right: 0;
  min-width: 220px;
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(24px) saturate(200%);
  -webkit-backdrop-filter: blur(24px) saturate(200%);
  border-radius: 16px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2), 0 0 0 1px rgba(255, 255, 255, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.4);
  padding: 0.5rem;
  z-index: 100;
  animation: fadeInDown 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.dark .user-dropdown {
  background: rgba(15, 23, 42, 0.4);
  border-color: rgba(255, 255, 255, 0.2);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.15);
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-sm);
  border: none;
  background: transparent;
  color: var(--text);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  text-align: left;
}

.dropdown-item:hover {
  background: rgba(0, 0, 0, 0.05);
}

.dark .dropdown-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.dropdown-item-danger {
  color: #ef4444;
}

.dropdown-item-danger:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
}

.dark .dropdown-item-danger:hover {
  background: rgba(239, 68, 68, 0.2);
}

.dropdown-item svg {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.dropdown-divider {
  height: 1px;
  background: var(--border);
  margin: 0.5rem 0;
}

/* 内容区域 */
.content-section {
  width: 100%;
  padding: 2.5rem 1.5rem;
  max-width: 1600px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

/* 加载和空状态 */
.loading-state,
.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  width: 100%;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

.empty-content {
  display: inline-block;
  padding: 3rem 2.5rem;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(24px) saturate(200%);
  -webkit-backdrop-filter: blur(24px) saturate(200%);
  border: 1px solid rgba(255, 255, 255, 0.4);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.empty-icon {
  width: 64px;
  height: 64px;
  color: var(--text-tertiary);
  margin: 0 auto 1rem;
}

/* 分类指示器 */
.category-indicators {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  padding: 0;
  width: 100%;
}

.category-btn-wrapper {
  position: relative;
  display: inline-block;
}

.category-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  min-width: 110px;
  border-radius: 9999px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  color: var(--text);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.category-btn:hover {
  background: rgba(255, 255, 255, 0.35);
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
  border-color: rgba(255, 255, 255, 0.5);
}

.category-btn.active {
  background: linear-gradient(135deg, var(--primary) 0%, #8b5cf6 100%);
  color: white;
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4), 0 0 0 2px rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  border-color: rgba(255, 255, 255, 0.5);
}

.category-edit-btn {
  position: absolute;
  top: -4px;
  right: -4px;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  color: var(--text-secondary);
  cursor: pointer;
  opacity: 0;
  transition: var(--transition);
  z-index: 10;
  font-size: 12px;
}

.category-btn-wrapper:hover .category-edit-btn {
  opacity: 1;
}

.category-edit-btn:hover {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}

/* 轮播容器 */
.content-area {
  position: relative;
  width: 100%;
}

.carousel-container {
  position: relative;
  overflow: hidden;
  min-height: 500px;
  width: 100%;
}

.carousel-track {
  display: flex;
  transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  width: 100%;
}

.carousel-slide {
  width: 100%;
  flex-shrink: 0;
  padding: 0;
}

/* 网站网格 */
.website-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  width: 100%;
}

@media (min-width: 640px) {
  .website-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 768px) {
  .website-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (min-width: 1024px) {
  .website-grid {
    grid-template-columns: repeat(5, 1fr);
  }
}

@media (min-width: 1280px) {
  .website-grid {
    grid-template-columns: repeat(6, 1fr);
  }
}

@media (min-width: 1536px) {
  .website-grid {
    grid-template-columns: repeat(7, 1fr);
  }
}

@media (min-width: 1920px) {
  .website-grid {
    grid-template-columns: repeat(8, 1fr);
  }
}

/* 网站卡片 */
.website-card-wrapper {
  position: relative;
  height: 100%;
}

.website-card {
  height: 100%;
  padding: 1.5rem;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  animation: fadeInUp 0.5s ease-out;
  position: relative;
  overflow: hidden;
}

.website-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
  opacity: 0;
  transition: opacity 0.4s ease;
  z-index: 0;
}

.website-card:hover::before {
  opacity: 1;
}

.website-card:hover {
  transform: translateY(-6px) scale(1.02);
  box-shadow: 0 20px 40px rgba(99, 102, 241, 0.3), 0 0 0 1px rgba(255, 255, 255, 0.5);
  border-color: rgba(255, 255, 255, 0.6);
}

.website-card:active {
  transform: translateY(-4px) scale(1.01);
}

.website-card > * {
  position: relative;
  z-index: 1;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.website-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  height: 100%;
}

.website-icon-wrapper {
  margin-bottom: 1rem;
  flex-shrink: 0;
}

.website-icon-bg {
  width: 72px;
  height: 72px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(15px) saturate(180%);
  -webkit-backdrop-filter: blur(15px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.2);
  transition: var(--transition-hover);
}

.website-card:hover .website-icon-bg {
  transform: scale(1.05);
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4);
  border-color: rgba(255, 255, 255, 0.3);
}

.website-icon-img {
  width: 48px;
  height: 48px;
  object-fit: contain;
  border-radius: var(--radius-sm);
}

.website-icon-svg {
  width: 48px;
  height: 48px;
  color: var(--primary);
}

.website-icon-text {
  color: var(--primary);
  font-weight: 700;
  font-size: 1.5rem;
}

.website-title {
  font-weight: 600;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
  color: var(--text);
  flex-shrink: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  width: 100%;
}

.website-description {
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
  flex: 1;
  min-height: 2.5rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.website-description-placeholder {
  flex: 1;
  min-height: 2.5rem;
}

.website-stats {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: var(--text-tertiary);
  flex-shrink: 0;
  margin-top: auto;
}

/* 网站卡片操作按钮 */
.website-action-btn {
  position: absolute;
  top: 0.75rem;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(15px) saturate(180%);
  -webkit-backdrop-filter: blur(15px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: var(--text);
  cursor: pointer;
  opacity: 0;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 10;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.website-card-wrapper:hover .website-action-btn {
  opacity: 1;
  transform: scale(1);
}

.favorite-btn {
  left: 0.75rem;
}

.favorite-btn:hover {
  background: rgba(251, 191, 36, 0.3);
  color: #f59e0b;
  border-color: rgba(251, 191, 36, 0.4);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(251, 191, 36, 0.3);
}

.favorite-btn:active {
  transform: translateY(0);
}

.star-filled {
  color: #f59e0b;
}

.edit-btn {
  right: 0.75rem;
}

.edit-btn:hover {
  background: rgba(99, 102, 241, 0.3);
  color: white;
  border-color: rgba(99, 102, 241, 0.4);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.3);
}

.edit-btn:active {
  transform: translateY(0);
}

.dark .website-action-btn {
  background: rgba(15, 23, 42, 0.4);
  border-color: rgba(255, 255, 255, 0.2);
}

/* 空常用列表 */
.empty-favorites {
  text-align: center;
  padding: 3rem 1rem;
  grid-column: 1 / -1;
}

/* 轮播导航 */
.carousel-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 2.5rem;
}

.carousel-nav-btn {
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(15px) saturate(180%);
  -webkit-backdrop-filter: blur(15px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: var(--text);
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.carousel-nav-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(99, 102, 241, 0.3);
  border-color: rgba(255, 255, 255, 0.4);
}

.carousel-nav-btn:active:not(:disabled) {
  transform: translateY(0);
}

.carousel-nav-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: scale(0.95);
}

.carousel-counter {
  padding: 0.75rem 1.5rem;
  border-radius: 9999px;
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.4);
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

/* 模态框 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
  padding: 1rem;
  animation: fadeIn 0.3s ease-out;
}

.modal {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(24px) saturate(200%);
  -webkit-backdrop-filter: blur(24px) saturate(200%);
  border-radius: 24px;
  padding: 2rem;
  width: 100%;
  max-width: 28rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(255, 255, 255, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.4);
  animation: fadeInUp 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.dark .modal {
  background: rgba(15, 23, 42, 0.4);
  border-color: rgba(255, 255, 255, 0.2);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.15);
}

.modal-large {
  max-width: 32rem;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--text);
}

.modal-divider {
  height: 1px;
  background: var(--border);
  margin: 1.25rem 0;
}

.modal-subtitle {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  color: var(--text);
}

.modal-form {
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

.form-hint {
  font-size: 0.75rem;
  color: var(--text-tertiary);
  margin-top: 0.25rem;
}

.form-error {
  color: #ef4444;
  font-size: 0.875rem;
}

.form-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.flex-1 {
  flex: 1;
}

.input-group {
  display: flex;
  gap: 0.5rem;
}

.btn-danger {
  background: #ef4444;
  color: white;
  border-color: #ef4444;
}

.btn-danger:hover {
  background: #dc2626;
  border-color: #dc2626;
}

/* 响应式 */
@media (max-width: 1024px) {
  .navbar-search {
    max-width: 300px;
  }
  
  .action-label {
    display: none;
  }
  
  .action-btn {
    padding: 0.5rem;
    min-width: 40px;
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .navbar-container {
    padding: 0 1rem;
    height: 64px;
  }
  
  .navbar-left {
    gap: 1rem;
  }
  
  .navbar-search {
    display: none;
  }
  
  .logo-text {
    font-size: 1rem;
  }
  
  .logo-icon {
    width: 36px;
    height: 36px;
    font-size: 1.125rem;
  }
  
  .user-menu {
    padding-left: 0.5rem;
    gap: 0.5rem;
  }
  
  .user-profile {
    padding: 0.25rem 0.5rem;
    gap: 0.5rem;
  }
  
  .user-avatar {
    width: 36px;
    height: 36px;
    font-size: 0.8125rem;
  }
  
  .user-dropdown {
    right: -0.5rem;
    min-width: 180px;
  }
}

@media (max-width: 640px) {
  .hidden-sm {
    display: none;
  }
  
  .navbar-container {
    gap: 1rem;
  }
  
  .action-buttons {
    gap: 0.25rem;
  }
  
  .content-section {
    padding: 1.5rem 1rem;
  }
}
</style>