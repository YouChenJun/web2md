#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
内容转换服务模块

提供 HTML 到 Markdown 格式转换功能。
"""

import re
import logging
from typing import Dict, Any, Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Comment
from markdownify import markdownify as md

from app.utils.exceptions import ConversionError


logger = logging.getLogger(__name__)


class ConverterService:
    """内容转换服务类"""
    
    def __init__(self):
        """初始化转换服务"""
        self.markdownify_options = {
            'heading_style': 'ATX',  # 使用 # 样式的标题
            'bullets': '-',  # 使用 - 作为列表项符号
            'emphasis_mark': '*',  # 使用 * 作为强调符号
            'strong_mark': '**',  # 使用 ** 作为加粗符号
            'default_title': True,  # 为链接添加默认标题
            'escape_asterisks': False,  # 不转义星号
            'escape_underscores': False,  # 不转义下划线
        }
    
    def convert_to_markdown(self, html_content: str, base_url: Optional[str] = None) -> Dict[str, Any]:
        """
        将 HTML 内容转换为 Markdown 格式
        
        Args:
            html_content (str): HTML 内容
            base_url (Optional[str]): 基础 URL，用于处理相对链接
            
        Returns:
            Dict[str, Any]: 转换结果，包含 Markdown 内容和统计信息
            
        Raises:
            ConversionError: 转换失败
        """
        try:
            logger.info("Starting HTML to Markdown conversion")
            
            if not html_content or not isinstance(html_content, str):
                raise ConversionError("HTML content cannot be empty")
            
            # 清理和预处理 HTML
            cleaned_html = self._clean_html(html_content)
            
            # 提取主要内容区域
            main_content = self._extract_main_content(cleaned_html)
            
            # 处理图片链接
            processed_html = self._process_images(main_content, base_url)
            
            # 转换为 Markdown
            markdown_content = self._html_to_markdown(processed_html)
            
            # 后处理 Markdown
            final_markdown = self._post_process_markdown(markdown_content)
            
            # 生成统计信息
            stats = self._generate_stats(html_content, final_markdown)
            
            logger.info("HTML to Markdown conversion completed successfully")
            
            return {
                'markdown': final_markdown,
                'stats': stats,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"HTML to Markdown conversion failed: {str(e)}")
            raise ConversionError(f"Conversion failed: {str(e)}")
    
    def _clean_html(self, html_content: str) -> str:
        """
        清理 HTML 内容，移除不需要的元素
        
        Args:
            html_content (str): 原始 HTML 内容
            
        Returns:
            str: 清理后的 HTML 内容
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 移除注释
            for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                comment.extract()
            
            # 移除脚本和样式
            for tag in soup(['script', 'style', 'noscript', 'meta', 'link']):
                tag.decompose()
            
            # 移除导航、页脚、侧边栏等非内容元素
            selectors_to_remove = [
                'nav', 'header', 'footer', 'aside',
                '.navigation', '.nav', '.navbar', '.menu',
                '.sidebar', '.side-bar', '.widget',
                '.advertisement', '.ads', '.ad',
                '.social', '.share', '.sharing',
                '.comments', '.comment-section',
                '.breadcrumb', '.breadcrumbs',
                '.pagination', '.pager',
                '.related', '.recommended',
                '.popup', '.modal', '.overlay'
            ]
            
            for selector in selectors_to_remove:
                for element in soup.select(selector):
                    element.decompose()
            
            # 移除空的段落和 div
            for tag in soup.find_all(['p', 'div']):
                if not tag.get_text(strip=True) and not tag.find(['img', 'video', 'audio']):
                    tag.decompose()
            
            return str(soup)
            
        except Exception as e:
            logger.warning(f"HTML cleaning failed: {str(e)}")
            return html_content
    
    def _extract_main_content(self, html_content: str) -> str:
        """
        提取页面主要内容区域
        
        Args:
            html_content (str): HTML 内容
            
        Returns:
            str: 主要内容的 HTML
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 尝试找到主要内容区域的常见选择器
            main_selectors = [
                'main',
                'article',
                '.main-content',
                '.content',
                '.post-content',
                '.entry-content',
                '.article-content',
                '#main',
                '#content',
                '.container .content',
                '[role="main"]'
            ]
            
            for selector in main_selectors:
                main_element = soup.select_one(selector)
                if main_element:
                    logger.debug(f"Found main content using selector: {selector}")
                    return str(main_element)
            
            # 如果没有找到特定的主内容区域，返回 body 内容
            body = soup.find('body')
            if body:
                return str(body)
            
            # 最后返回整个文档
            return html_content
            
        except Exception as e:
            logger.warning(f"Main content extraction failed: {str(e)}")
            return html_content
    
    def _process_images(self, html_content: str, base_url: Optional[str] = None) -> str:
        """
        处理图片链接，确保使用绝对 URL
        
        Args:
            html_content (str): HTML 内容
            base_url (Optional[str]): 基础 URL
            
        Returns:
            str: 处理后的 HTML 内容
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            for img in soup.find_all('img'):
                src = img.get('src')
                if not src:
                    continue
                
                # 跳过 data URL
                if src.startswith('data:'):
                    continue
                
                # 处理相对 URL
                if base_url and not src.startswith(('http://', 'https://')):
                    absolute_url = urljoin(base_url, src)
                    img['src'] = absolute_url
                
                # 添加 alt 属性（如果没有的话）
                if not img.get('alt'):
                    # 尝试从文件名生成 alt 文本
                    try:
                        filename = urlparse(img['src']).path.split('/')[-1]
                        if filename:
                            alt_text = filename.split('.')[0].replace('-', ' ').replace('_', ' ')
                            img['alt'] = alt_text
                    except Exception:
                        img['alt'] = 'Image'
            
            return str(soup)
            
        except Exception as e:
            logger.warning(f"Image processing failed: {str(e)}")
            return html_content
    
    def _html_to_markdown(self, html_content: str) -> str:
        """
        将 HTML 转换为 Markdown
        
        Args:
            html_content (str): HTML 内容
            
        Returns:
            str: Markdown 内容
        """
        try:
            # 使用 markdownify 进行转换
            markdown = md(
                html_content,
                **self.markdownify_options
            )
            
            return markdown
            
        except Exception as e:
            logger.error(f"Markdownify conversion failed: {str(e)}")
            raise ConversionError(f"Markdown conversion failed: {str(e)}")
    
    def _post_process_markdown(self, markdown_content: str) -> str:
        """
        后处理 Markdown 内容，优化格式
        
        Args:
            markdown_content (str): 原始 Markdown 内容
            
        Returns:
            str: 优化后的 Markdown 内容
        """
        try:
            # 移除多余的空行
            markdown = re.sub(r'\n\s*\n\s*\n', '\n\n', markdown_content)
            
            # 修复列表格式
            markdown = re.sub(r'\n(\s*[-*+])', r'\n\n\1', markdown)
            
            # 修复标题格式
            markdown = re.sub(r'\n(#{1,6}\s)', r'\n\n\1', markdown)
            
            # 修复代码块格式
            markdown = re.sub(r'\n(```)', r'\n\n\1', markdown)
            
            # 移除行首尾空白
            lines = [line.rstrip() for line in markdown.split('\n')]
            markdown = '\n'.join(lines)
            
            # 确保文档以换行符结尾
            if not markdown.endswith('\n'):
                markdown += '\n'
            
            return markdown
            
        except Exception as e:
            logger.warning(f"Markdown post-processing failed: {str(e)}")
            return markdown_content
    
    def _generate_stats(self, html_content: str, markdown_content: str) -> Dict[str, Any]:
        """
        生成转换统计信息
        
        Args:
            html_content (str): 原始 HTML 内容
            markdown_content (str): 转换后的 Markdown 内容
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            # HTML 统计
            html_soup = BeautifulSoup(html_content, 'html.parser')
            html_text = html_soup.get_text()
            
            # 统计信息
            stats = {
                'html_length': len(html_content),
                'markdown_length': len(markdown_content),
                'html_text_length': len(html_text),
                'markdown_text_length': len(markdown_content.replace('#', '').replace('*', '').replace('`', '')),
                'compression_ratio': len(markdown_content) / len(html_content) if html_content else 0,
                'image_count': len(html_soup.find_all('img')),
                'link_count': len(html_soup.find_all('a')),
                'heading_count': len(html_soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
                'paragraph_count': len(html_soup.find_all('p')),
                'list_count': len(html_soup.find_all(['ul', 'ol'])),
                'table_count': len(html_soup.find_all('table'))
            }
            
            return stats
            
        except Exception as e:
            logger.warning(f"Stats generation failed: {str(e)}")
            return {}