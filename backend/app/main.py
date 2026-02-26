from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api import auth, categories, websites
import sqlite3
import os

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 数据库迁移
def migrate_database():
    """执行数据库迁移"""
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./navigate.db")
    if DATABASE_URL.startswith("sqlite:///"):
        # 处理相对路径和绝对路径
        db_path = DATABASE_URL.replace("sqlite:///", "")
        if not os.path.isabs(db_path):
            # 如果是相对路径，确保目录存在
            db_dir = os.path.dirname(db_path) if os.path.dirname(db_path) else "."
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 迁移1: 添加 is_favorite 列到 websites 表
            cursor.execute("PRAGMA table_info(websites)")
            website_columns = [column[1] for column in cursor.fetchall()]
            if 'is_favorite' not in website_columns:
                cursor.execute("ALTER TABLE websites ADD COLUMN is_favorite INTEGER DEFAULT 0")
                print("✓ 已添加 is_favorite 列到 websites 表")
            
            # 迁移2: 将 username 改为 display_name（如果存在 username 列）
            cursor.execute("PRAGMA table_info(users)")
            user_columns = [column[1] for column in cursor.fetchall()]
            if 'username' in user_columns and 'display_name' not in user_columns:
                # 添加 display_name 列
                cursor.execute("ALTER TABLE users ADD COLUMN display_name VARCHAR(50)")
                # 将 username 的值复制到 display_name
                cursor.execute("UPDATE users SET display_name = username WHERE display_name IS NULL")
                # 设置默认值
                cursor.execute("UPDATE users SET display_name = email WHERE display_name IS NULL OR display_name = ''")
                print("✓ 已迁移 username 到 display_name")
            # 迁移3: 若表同时有 username 和 display_name，将空的 username 填为 display_name
            if 'username' in user_columns and 'display_name' in user_columns:
                cursor.execute("UPDATE users SET username = display_name WHERE username IS NULL OR username = ''")
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"迁移警告: {str(e)}")

migrate_database()

app = FastAPI(
    title="网站导航管理系统 API",
    description="一个美观的网站导航管理系统后端 API",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(categories.router, prefix="/api/categories", tags=["分类"])
app.include_router(websites.router, prefix="/api/websites", tags=["网站"])

@app.get("/")
async def root():
    return {"message": "网站导航管理系统 API"}

@app.get("/api/health")
async def health():
    return {"status": "ok"}
