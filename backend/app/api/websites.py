from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.database import get_db
from app.models import Website, User, Category
from app.schemas import WebsiteCreate, WebsiteUpdate, WebsiteResponse
from app.auth.dependencies import get_current_user
from app.services.website_scraper import scrape_website_info

router = APIRouter()

@router.get("", response_model=List[WebsiteResponse])
async def get_websites(
    category_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    favorites_only: Optional[bool] = Query(None, description="只获取常用网站"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Website).filter(Website.user_id == current_user.id)
    
    if category_id:
        query = query.filter(Website.category_id == category_id)
    
    if favorites_only:
        query = query.filter(Website.is_favorite == 1)
    
    if search:
        query = query.filter(
            or_(
                Website.title.ilike(f"%{search}%"),
                Website.url.ilike(f"%{search}%"),
                Website.description.ilike(f"%{search}%")
            )
        )
    
    websites = query.order_by(Website.sort_order, Website.created_at).all()
    return websites

@router.post("", response_model=WebsiteResponse, status_code=status.HTTP_201_CREATED)
async def create_website(
    website_data: WebsiteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 验证分类是否存在且属于当前用户
    category = db.query(Category).filter(
        Category.id == website_data.category_id,
        Category.user_id == current_user.id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # 如果标题或图标为空，尝试自动抓取
    website_dict = website_data.dict()
    if not website_dict.get('title') or not website_dict.get('icon'):
        scraped_info = scrape_website_info(website_dict['url'])
        if not website_dict.get('title') and scraped_info.get('title'):
            website_dict['title'] = scraped_info['title']
        if not website_dict.get('icon') and scraped_info.get('icon'):
            website_dict['icon'] = scraped_info['icon']
        if not website_dict.get('description') and scraped_info.get('description'):
            website_dict['description'] = scraped_info['description']
    
    db_website = Website(
        **website_dict,
        user_id=current_user.id
    )
    db.add(db_website)
    db.commit()
    db.refresh(db_website)
    return db_website

@router.put("/{website_id}", response_model=WebsiteResponse)
async def update_website(
    website_id: int,
    website_data: WebsiteUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_website = db.query(Website).filter(
        Website.id == website_id,
        Website.user_id == current_user.id
    ).first()
    
    if not db_website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Website not found"
        )
    
    # 如果更新了分类，验证新分类是否存在
    if website_data.category_id is not None:
        category = db.query(Category).filter(
            Category.id == website_data.category_id,
            Category.user_id == current_user.id
        ).first()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
    
    update_data = website_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_website, field, value)
    
    db.commit()
    db.refresh(db_website)
    return db_website

@router.delete("/{website_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_website(
    website_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_website = db.query(Website).filter(
        Website.id == website_id,
        Website.user_id == current_user.id
    ).first()
    
    if not db_website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Website not found"
        )
    
    db.delete(db_website)
    db.commit()
    return None

@router.post("/{website_id}/click", response_model=WebsiteResponse)
async def record_click(
    website_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_website = db.query(Website).filter(
        Website.id == website_id,
        Website.user_id == current_user.id
    ).first()
    
    if not db_website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Website not found"
        )
    
    db_website.click_count += 1
    db.commit()
    db.refresh(db_website)
    return db_website

@router.post("/{website_id}/toggle-favorite", response_model=WebsiteResponse)
async def toggle_favorite(
    website_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """切换网站的常用状态"""
    db_website = db.query(Website).filter(
        Website.id == website_id,
        Website.user_id == current_user.id
    ).first()
    
    if not db_website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Website not found"
        )
    
    db_website.is_favorite = 1 if db_website.is_favorite == 0 else 0
    db.commit()
    db.refresh(db_website)
    return db_website

@router.get("/scrape", response_model=dict)
async def scrape_website(
    url: str = Query(..., description="要抓取的网站URL"),
    current_user: User = Depends(get_current_user)
):
    """
    抓取网站信息（标题、图标、描述）
    """
    try:
        info = scrape_website_info(url)
        return info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"抓取网站信息失败: {str(e)}"
        )
