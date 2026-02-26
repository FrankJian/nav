# 网站导航管理系统

一个美观的网站导航管理系统，参考 sun-panel 的设计风格，用于管理和快速访问常用网站。

## 技术栈

- **前端**: Vue 3 (JavaScript) + Vite + Vue Router + Pinia + Tailwind CSS
- **后端**: FastAPI + SQLAlchemy + SQLite/PostgreSQL
- **部署**: Docker + Docker Compose

## 功能特性

- 用户认证（注册/登录）
- 网站管理（添加/编辑/删除）
- 分类管理
- 卡片式布局展示
- 搜索功能
- 点击统计
- 响应式设计
- 深色/浅色主题

## 快速开始

### 使用 Docker Compose（推荐）

1. 克隆或下载项目
2. 在项目根目录运行：

```bash
docker-compose up -d
```

3. 访问 http://localhost:3000

4. 首次使用需要注册账号

### 不使用 Docker 一键启动

在已安装 **Python 3**、**Node 18+** 的前提下：

1. 安装后端依赖（首次或依赖变更时）：
   ```bash
   pip install -r backend/requirements.txt
   ```
2. 在项目根目录执行：
   ```bash
   ./start.sh
   ```
3. 浏览器访问 **http://127.0.0.1:5173**（前端由 Vite 提供，`/api` 已代理到后端 8000 端口）。

按 `Ctrl+C` 会同时停止前后端。数据库文件位于 `./data/navigate.db`，可选复制 `.env.example` 为 `.env` 后修改 `SECRET_KEY`、`DATABASE_URL`。

### 本地开发（分别启动）

#### 后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端 API 文档：http://localhost:8000/docs

#### 前端

```bash
cd frontend
npm install
npm run dev
```

前端开发服务器：http://localhost:5173

## 功能说明

### 主要功能

1. **用户认证**
   - 用户注册/登录
   - JWT Token 认证
   - 密码加密存储

2. **分类管理**
   - 创建、编辑、删除分类
   - 轮播图形式展示，每个页面显示一个分类
   - 鼠标滚轮切换分类

3. **网站管理**
   - 添加、编辑、删除网站
   - 自动抓取网站信息（标题、图标、描述）
   - 支持自定义图标（Iconify 或 URL）
   - 点击统计
   - 搜索功能
   - 常用网站标记

4. **界面特性**
   - 卡片式布局（参考 sun-panel 设计）
   - 轮播图展示分类
   - 深色/浅色主题切换
   - 响应式设计
   - 半透明效果和渐变背景
   - 图标库支持（Iconify）

## 图标使用

系统支持使用 Iconify 图标库，在添加分类或网站时，可以输入图标名称，例如：
- `mdi:home` - Material Design Icons
- `mdi:github` - GitHub 图标
- `mdi:web` - 网页图标

更多图标请访问：https://icon-sets.iconify.design/

## 项目结构

```
navigate/
├── frontend/              # Vue3 前端应用
│   ├── src/
│   │   ├── views/         # 页面组件
│   │   ├── router/        # 路由配置
│   │   ├── stores/        # Pinia 状态管理
│   │   └── api/           # API 调用
│   ├── Dockerfile         # 前端镜像（构建 + nginx）
│   ├── nginx.conf         # 前端 nginx 配置（/api 代理到 backend）
│   └── package.json
├── backend/               # FastAPI 后端应用
│   ├── app/
│   │   ├── api/           # API 路由
│   │   ├── auth/          # 认证模块
│   │   ├── services/      # 业务服务
│   │   └── main.py        # 应用入口
│   ├── Dockerfile         # 后端镜像
│   └── requirements.txt
├── docker-compose.yml      # Docker Compose 配置（前后端两服务）
├── docker-entrypoint.sh    # 后端启动脚本（迁移 + 启动）
└── README.md
```

## License

MIT
