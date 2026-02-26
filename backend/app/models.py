from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=True)  # 兼容旧表，新建用户用 display_name 填充
    display_name = Column(String(50), nullable=False)  # 显示名
    email = Column(String(100), unique=True, index=True, nullable=False)  # 邮箱作为唯一标识
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")
    websites = relationship("Website", back_populates="user", cascade="all, delete-orphan")

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    icon = Column(String(100))
    color = Column(String(20))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="categories")
    websites = relationship("Website", back_populates="category", cascade="all, delete-orphan")

class Website(Base):
    __tablename__ = "websites"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    url = Column(String(500), nullable=False)
    icon = Column(String(500))
    description = Column(Text)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sort_order = Column(Integer, default=0)
    click_count = Column(Integer, default=0)
    is_favorite = Column(Integer, default=0)  # 0: 不常用, 1: 常用
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="websites")
    category = relationship("Category", back_populates="websites")
