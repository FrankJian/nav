from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional

# User Schemas
class UserBase(BaseModel):
    display_name: str
    email: EmailStr

class UserCreate(BaseModel):
    display_name: str
    email: EmailStr
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('密码长度至少为6位')
        if len(v.encode('utf-8')) > 72:
            raise ValueError('密码长度不能超过72字节')
        return v

class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Category Schemas
class CategoryBase(BaseModel):
    name: str
    icon: Optional[str] = None
    color: Optional[str] = None
    sort_order: int = 0

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    sort_order: Optional[int] = None

class CategoryResponse(CategoryBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Website Schemas
class WebsiteBase(BaseModel):
    title: str
    url: str
    icon: Optional[str] = None
    description: Optional[str] = None
    category_id: int
    sort_order: int = 0

class WebsiteCreate(WebsiteBase):
    pass

class WebsiteUpdate(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    sort_order: Optional[int] = None

class WebsiteResponse(WebsiteBase):
    id: int
    user_id: int
    click_count: int
    is_favorite: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class PasswordChange(BaseModel):
    """修改密码：需提供当前密码和新密码"""
    current_password: str
    new_password: str

    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 6:
            raise ValueError('新密码长度至少为6位')
        if len(v.encode('utf-8')) > 72:
            raise ValueError('新密码长度不能超过72字节')
        return v
