#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
自定义异常类模块

定义应用中使用的各种自定义异常类。
"""


class WebToMarkdownError(Exception):
    """Web 到 Markdown 转换服务的基础异常类"""
    
    def __init__(self, message: str, status_code: int = 500):
        """
        初始化异常
        
        Args:
            message (str): 错误消息
            status_code (int): HTTP 状态码
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class URLValidationError(WebToMarkdownError):
    """URL 验证错误"""
    
    def __init__(self, message: str = "Invalid URL"):
        super().__init__(message, 400)


class SecurityError(WebToMarkdownError):
    """安全验证错误"""
    
    def __init__(self, message: str = "Security validation failed"):
        super().__init__(message, 403)


class RenderingError(WebToMarkdownError):
    """网页渲染错误"""
    
    def __init__(self, message: str = "Failed to render webpage"):
        super().__init__(message, 500)


class ConversionError(WebToMarkdownError):
    """内容转换错误"""
    
    def __init__(self, message: str = "Failed to convert content to Markdown"):
        super().__init__(message, 500)


class TimeoutError(WebToMarkdownError):
    """超时错误"""
    
    def __init__(self, message: str = "Request timeout"):
        super().__init__(message, 408)


class NetworkError(WebToMarkdownError):
    """网络错误"""
    
    def __init__(self, message: str = "Network error occurred"):
        super().__init__(message, 502)


class ContentNotFoundError(WebToMarkdownError):
    """内容未找到错误"""
    
    def __init__(self, message: str = "Content not found"):
        super().__init__(message, 404)