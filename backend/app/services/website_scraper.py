import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

def scrape_website_info(url: str) -> Dict[str, Optional[str]]:
    """
    抓取网站信息：标题、图标、描述
    
    Args:
        url: 网站URL
        
    Returns:
        包含 title, icon, description 的字典
    """
    try:
        # 确保URL有协议
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # 设置请求头，模拟浏览器
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        
        # 发送请求，设置超时
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        response.raise_for_status()
        response.encoding = response.apparent_encoding or 'utf-8'
        
        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 获取标题
        title = None
        if soup.title:
            title = soup.title.string.strip() if soup.title.string else None
        
        # 如果没有title标签，尝试从og:title获取
        if not title:
            og_title = soup.find('meta', property='og:title')
            if og_title and og_title.get('content'):
                title = og_title.get('content').strip()
        
        # 获取描述
        description = None
        meta_description = soup.find('meta', attrs={'name': 'description'})
        if meta_description and meta_description.get('content'):
            description = meta_description.get('content').strip()
        
        # 如果没有description，尝试从og:description获取
        if not description:
            og_description = soup.find('meta', property='og:description')
            if og_description and og_description.get('content'):
                description = og_description.get('content').strip()
        
        # 获取图标
        icon = None
        
        # 1. 尝试获取 favicon.ico
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        favicon_url = urljoin(base_url, '/favicon.ico')
        
        # 验证favicon是否存在
        try:
            favicon_response = requests.head(favicon_url, timeout=5, allow_redirects=True)
            if favicon_response.status_code == 200:
                icon = favicon_url
        except:
            pass
        
        # 2. 尝试从link标签获取
        if not icon:
            # 查找apple-touch-icon
            apple_icon = soup.find('link', rel='apple-touch-icon')
            if apple_icon and apple_icon.get('href'):
                icon = urljoin(url, apple_icon.get('href'))
            else:
                # 查找icon
                icon_link = soup.find('link', rel='icon') or soup.find('link', rel='shortcut icon')
                if icon_link and icon_link.get('href'):
                    icon = urljoin(url, icon_link.get('href'))
        
        # 3. 尝试从og:image获取
        if not icon:
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                icon = urljoin(url, og_image.get('content'))
        
        # 如果找到了图标，确保是完整URL
        if icon and not icon.startswith(('http://', 'https://')):
            icon = urljoin(url, icon)
        
        # 清理描述（移除多余空白）
        if description:
            description = re.sub(r'\s+', ' ', description).strip()
            # 限制描述长度
            if len(description) > 200:
                description = description[:200] + '...'
        
        return {
            'title': title or '未命名网站',
            'icon': icon,
            'description': description
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"请求网站失败: {url}, 错误: {str(e)}")
        return {
            'title': None,
            'icon': None,
            'description': None
        }
    except Exception as e:
        logger.error(f"抓取网站信息失败: {url}, 错误: {str(e)}")
        return {
            'title': None,
            'icon': None,
            'description': None
        }
