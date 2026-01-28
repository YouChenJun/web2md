#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
网页渲染服务模块

使用 Playwright 控制 Chromium 浏览器渲染网页内容。
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from urllib.parse import urljoin, urlparse

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, TimeoutError as PlaywrightTimeoutError

from config.settings import Config
from app.utils.exceptions import RenderingError, TimeoutError, NetworkError


logger = logging.getLogger(__name__)


class RendererService:
    """网页渲染服务类"""
    
    def __init__(self):
        """初始化渲染服务"""
        self.config = Config()
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self._playwright = None
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.setup_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.cleanup_browser()
    
    async def setup_browser(self) -> None:
        """初始化浏览器实例"""
        try:
            logger.info("Setting up Playwright browser")
            
            self._playwright = await async_playwright().start()
            
            # 启动 Chromium 浏览器
            self.browser = await self._playwright.chromium.launch(
                headless=self.config.PLAYWRIGHT_HEADLESS,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--no-first-run',
                    '--no-default-browser-check',
                    '--disable-default-apps',
                    '--disable-extensions',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--disable-features=TranslateUI',
                    '--disable-ipc-flooding-protection'
                ]
            )
            
            # 创建浏览器上下文
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            logger.info("Playwright browser setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup browser: {str(e)}")
            raise RenderingError(f"Browser setup failed: {str(e)}")
    
    async def cleanup_browser(self) -> None:
        """清理浏览器资源"""
        try:
            logger.info("Cleaning up browser resources")
            
            if self.context:
                await self.context.close()
                self.context = None
            
            if self.browser:
                await self.browser.close()
                self.browser = None
            
            if self._playwright:
                await self._playwright.stop()
                self._playwright = None
            
            logger.info("Browser cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during browser cleanup: {str(e)}")
    
    async def render_page(self, url: str, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        渲染页面并返回内容
        
        Args:
            url (str): 要渲染的 URL
            timeout (Optional[int]): 超时时间（毫秒），默认使用配置值
            
        Returns:
            Dict[str, Any]: 渲染结果，包含 HTML 内容和元数据
            
        Raises:
            RenderingError: 渲染失败
            TimeoutError: 渲染超时
            NetworkError: 网络错误
        """
        if not self.context:
            raise RenderingError("Browser not initialized")
        
        timeout_ms = timeout or self.config.PLAYWRIGHT_TIMEOUT
        page: Optional[Page] = None
        
        try:
            logger.info(f"Starting to render page: {url}")
            
            # 创建新页面
            page = await self.context.new_page()
            
            # 设置页面事件监听
            await self._setup_page_listeners(page)
            
            # 导航到目标页面
            response = await page.goto(
                url,
                wait_until='domcontentloaded',
                timeout=timeout_ms
            )
            
            if not response:
                raise NetworkError(f"Failed to load page: {url}")
            
            # 检查响应状态
            if response.status >= 400:
                raise NetworkError(f"HTTP {response.status}: {response.status_text}")
            
            # 等待页面完全加载
            await self._wait_for_page_load(page, timeout_ms)
            
            # 获取页面内容
            html_content = await page.content()
            
            # 获取页面元数据
            metadata = await self._extract_metadata(page)
            
            # 处理相对 URL
            processed_html = await self._process_relative_urls(html_content, url)
            
            logger.info(f"Page rendering completed successfully: {url}")
            
            return {
                'html': processed_html,
                'url': url,
                'title': metadata.get('title', ''),
                'description': metadata.get('description', ''),
                'status_code': response.status,
                'final_url': page.url,
                'content_length': len(processed_html)
            }
            
        except PlaywrightTimeoutError as e:
            logger.error(f"Page rendering timeout for {url}: {str(e)}")
            raise TimeoutError(f"Page rendering timeout: {str(e)}")
        
        except Exception as e:
            logger.error(f"Page rendering failed for {url}: {str(e)}")
            if "net::" in str(e) or "DNS" in str(e):
                raise NetworkError(f"Network error: {str(e)}")
            else:
                raise RenderingError(f"Rendering failed: {str(e)}")
        
        finally:
            if page:
                try:
                    await page.close()
                except Exception as e:
                    logger.warning(f"Error closing page: {str(e)}")
    
    async def _setup_page_listeners(self, page: Page) -> None:
        """设置页面事件监听器"""
        
        # 监听控制台消息
        page.on("console", lambda msg: logger.debug(f"Console {msg.type}: {msg.text}"))
        
        # 监听页面错误
        page.on("pageerror", lambda error: logger.warning(f"Page error: {error}"))
        
        # 监听请求失败
        page.on("requestfailed", lambda request: logger.warning(f"Request failed: {request.url}"))
    
    async def _wait_for_page_load(self, page: Page, timeout_ms: int) -> None:
        """等待页面完全加载"""
        try:
            # 等待网络空闲
            await page.wait_for_load_state('networkidle', timeout=timeout_ms)
            
            # 等待一小段时间确保动态内容加载完成
            await asyncio.sleep(1)
            
        except PlaywrightTimeoutError:
            logger.warning("Page load timeout, continuing with current content")
    
    async def _extract_metadata(self, page: Page) -> Dict[str, str]:
        """提取页面元数据"""
        try:
            metadata = {}
            
            # 获取页面标题
            title = await page.title()
            if title:
                metadata['title'] = title
            
            # 获取描述
            description_element = await page.query_selector('meta[name="description"]')
            if description_element:
                description = await description_element.get_attribute('content')
                if description:
                    metadata['description'] = description
            
            # 获取关键词
            keywords_element = await page.query_selector('meta[name="keywords"]')
            if keywords_element:
                keywords = await keywords_element.get_attribute('content')
                if keywords:
                    metadata['keywords'] = keywords
            
            return metadata
            
        except Exception as e:
            logger.warning(f"Failed to extract metadata: {str(e)}")
            return {}
    
    async def _process_relative_urls(self, html_content: str, base_url: str) -> str:
        """处理相对 URL，转换为绝对 URL"""
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 处理图片 src 属性
            for img in soup.find_all('img', src=True):
                src = img['src']
                if not src.startswith(('http://', 'https://', 'data:')):
                    absolute_url = urljoin(base_url, src)
                    img['src'] = absolute_url
            
            # 处理链接 href 属性
            for link in soup.find_all('a', href=True):
                href = link['href']
                if not href.startswith(('http://', 'https://', 'mailto:', 'tel:', '#')):
                    absolute_url = urljoin(base_url, href)
                    link['href'] = absolute_url
            
            return str(soup)
            
        except Exception as e:
            logger.warning(f"Failed to process relative URLs: {str(e)}")
            return html_content