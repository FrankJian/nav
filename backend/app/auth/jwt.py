from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
import os

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # 确保密码是字符串格式
    if isinstance(plain_password, bytes):
        plain_password = plain_password.decode('utf-8')
    plain_password = str(plain_password)
    
    # 确保密码不超过 72 字节
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # 使用 bcrypt 验证密码
    try:
        return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    # 确保密码是字符串格式
    if isinstance(password, bytes):
        password = password.decode('utf-8')
    password = str(password)
    
    # bcrypt 限制密码长度为 72 字节（UTF-8 编码后）
    # 如果密码超过 72 字节，进行截断
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        # 截断到 72 字节
        password_bytes = password_bytes[:72]
    
    # 使用 bcrypt 生成哈希，rounds=12 是默认值
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
