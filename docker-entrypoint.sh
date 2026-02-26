#!/bin/bash
set -e

# 确保数据目录存在
mkdir -p /app/data
chmod 755 /app/data

# 设置数据库路径
export DATABASE_URL=${DATABASE_URL:-"sqlite:////app/data/navigate.db"}

# 运行数据库迁移（如果需要）
cd /app/backend
python3 -c "
import sqlite3
import os
db_url = os.getenv('DATABASE_URL', 'sqlite:////app/data/navigate.db')
if db_url.startswith('sqlite:///'):
    db_path = db_url.replace('sqlite:///', '')
    # 确保数据库文件目录存在
    db_dir = os.path.dirname(db_path) if os.path.dirname(db_path) else '.'
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    # 如果数据库文件存在，执行迁移
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 迁移1: 添加 is_favorite 列
            cursor.execute('PRAGMA table_info(websites)')
            website_columns = [col[1] for col in cursor.fetchall()]
            if 'is_favorite' not in website_columns:
                cursor.execute('ALTER TABLE websites ADD COLUMN is_favorite INTEGER DEFAULT 0')
                print('✓ 已添加 is_favorite 列到 websites 表')
            
            # 迁移2: username 改为 display_name
            cursor.execute('PRAGMA table_info(users)')
            user_columns = [col[1] for col in cursor.fetchall()]
            if 'username' in user_columns and 'display_name' not in user_columns:
                cursor.execute('ALTER TABLE users ADD COLUMN display_name VARCHAR(50)')
                cursor.execute('UPDATE users SET display_name = username WHERE display_name IS NULL')
                cursor.execute('UPDATE users SET display_name = email WHERE display_name IS NULL OR display_name = \"\"')
                print('✓ 已迁移 username 到 display_name')
            
            conn.commit()
            conn.close()
            print('✓ 数据库迁移完成')
        except Exception as e:
            print(f'数据库迁移警告: {e}')
    else:
        print('数据库文件不存在，将在首次运行时创建')
"

# 执行传入的命令
exec "$@"
