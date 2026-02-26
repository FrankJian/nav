# 前端：构建阶段（构建时 context 为项目根目录）
FROM node:24-alpine AS builder

WORKDIR /app

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ .
RUN npm run build

# 前端：运行阶段（仅 nginx 提供静态资源并代理 /api）
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 使用前端专用 nginx 配置（/api 代理到 backend 服务）
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
