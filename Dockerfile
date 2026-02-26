# 多阶段构建：前端构建阶段
FROM node:24-alpine AS frontend-builder

WORKDIR /app/frontend

# 复制前端依赖文件
COPY frontend/package*.json ./

# 安装前端依赖
RUN npm install

# 复制前端源代码
COPY frontend/ .

# 构建前端应用
RUN npm run build

# 多阶段构建：后端准备阶段
FROM python:3.13-slim AS backend-builder

WORKDIR /app/backend

# 复制后端依赖文件
COPY backend/requirements.txt .

# 安装后端依赖
RUN pip install --no-cache-dir -r requirements.txt

# 最终阶段：运行环境
FROM python:3.13-slim

# 安装 Nginx 和 Supervisor
RUN apt-get update && \
    apt-get install -y nginx supervisor && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 从后端构建阶段复制 Python 依赖
COPY --from=backend-builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# 复制后端应用代码
COPY backend/ ./backend/

# 从前端构建阶段复制构建产物
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html

# 复制 Nginx 配置
COPY nginx.conf /etc/nginx/sites-available/default
RUN ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default && \
    rm -f /etc/nginx/sites-enabled/default.conf

# 复制 Supervisor 配置
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# 创建数据目录和日志目录
RUN mkdir -p /app/data /var/log/fastapi /var/log/nginx && \
    chmod -R 755 /app/data && \
    chown -R www-data:www-data /var/log/nginx

# 暴露端口
EXPOSE 80

# 复制启动脚本
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# 使用 Supervisor 管理进程
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
