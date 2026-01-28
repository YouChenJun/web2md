#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Flask 路由模块

定义 Web 服务的 API 路由和请求处理逻辑。
"""

import asyncio
import logging
from flask import Blueprint, request, jsonify, Response
from functools import wraps
from typing import Dict, Any, Tuple, Callable
from werkzeug.exceptions import Unauthorized

from app.services.security import SecurityService
from app.services.renderer import RendererService
from app.services.converter import ConverterService
from app.utils.exceptions import (
    WebToMarkdownError, URLValidationError, SecurityError,
    RenderingError, ConversionError, TimeoutError, NetworkError,
    ContentNotFoundError
)
from config.settings import Config


logger = logging.getLogger(__name__)

# 创建蓝图
main_bp = Blueprint('main', __name__)

# 初始化服务
security_service = SecurityService()
converter_service = ConverterService()
config = Config()


def require_bearer_token(f: Callable) -> Callable:
    """
    Bearer Token 认证装饰器
    
    Args:
        f: 被装饰的函数
        
    Returns:
        Callable: 包装后的函数
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 如果未启用 Bearer 认证，直接通过
        if not config.ENABLE_BEARER_AUTH:
            return f(*args, **kwargs)
        
        # 检查是否配置了 Bearer Token
        if not config.BEARER_TOKEN:
            logger.warning("Bearer token not configured")
            return _create_error_response(
                "Authentication is required but not configured",
                500
            )
        
        # 从 Authorization header 获取 token
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            logger.warning("Missing Authorization header")
            return _create_error_response(
                "Missing Authorization header",
                401
            )
        
        # 验证 Bearer Token 格式
        if not auth_header.startswith('Bearer '):
            logger.warning("Invalid Authorization header format")
            return _create_error_response(
                "Invalid Authorization header format. Expected: 'Bearer <token>'",
                401
            )
        
        token = auth_header[7:]  # 移除 'Bearer ' 前缀
        
        # 验证 token
        if token != config.BEARER_TOKEN:
            logger.warning("Invalid Bearer token provided")
            return _create_error_response(
                "Invalid or expired Bearer token",
                401
            )
        
        logger.info("Bearer token authentication successful")
        return f(*args, **kwargs)
    
    return decorated_function


@main_bp.route('/target', methods=['GET'])
@require_bearer_token
def convert_url_to_markdown() -> Response:
    """
    将指定 URL 的网页内容转换为 Markdown 格式
    
    查询参数:
        url (str): 要转换的目标 URL
        
    返回:
        Response: Markdown 内容或错误信息
    """
    try:
        # 获取 URL 参数
        target_url = request.args.get('url')
        
        if not target_url:
            logger.warning("Missing URL parameter in request")
            return _create_error_response(
                "Missing required parameter 'url'",
                400
            )
        
        logger.info(f"Processing conversion request for URL: {target_url}")
        
        # 安全验证
        try:
            validation_result = security_service.validate_url(target_url)
            logger.info(f"URL validation passed for: {target_url}")
        except (URLValidationError, SecurityError) as e:
            logger.warning(f"URL validation failed for {target_url}: {str(e)}")
            return _create_error_response(str(e), e.status_code)
        
        # 异步处理网页渲染和转换
        try:
            result = asyncio.run(_process_url_conversion(target_url))
            
            if not result['success']:
                return _create_error_response(
                    result.get('error', 'Conversion failed'),
                    result.get('status_code', 500)
                )
            
            # 返回 Markdown 内容
            markdown_content = result['markdown']
            
            logger.info(f"Conversion completed successfully for: {target_url}")
            
            return Response(
                markdown_content,
                mimetype='text/plain',
                headers={
                    'Content-Type': 'text/plain; charset=utf-8',
                    'X-Original-URL': target_url,
                    'X-Content-Length': str(len(markdown_content)),
                    'X-Conversion-Stats': str(result.get('stats', {}))
                }
            )
            
        except Exception as e:
            logger.error(f"Unexpected error during conversion for {target_url}: {str(e)}")
            return _create_error_response(
                "Internal server error occurred",
                500
            )
    
    except Exception as e:
        logger.error(f"Unexpected error in route handler: {str(e)}")
        return _create_error_response("Internal server error", 500)


@main_bp.route('/health', methods=['GET'])
def health_check() -> Response:
    """
    健康检查端点
    
    返回:
        Response: 服务状态信息
    """
    try:
        health_info = {
            'status': 'healthy',
            'service': 'web-to-markdown',
            'version': '1.0.0',
            'endpoints': {
                '/target': 'Convert URL to Markdown',
                '/health': 'Health check'
            }
        }
        
        return jsonify(health_info)
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return _create_error_response("Health check failed", 500)


@main_bp.route('/', methods=['GET'])
def index() -> Response:
    """
    根路径，返回服务信息
    
    返回:
        Response: 服务使用说明
    """
    try:
        service_info = {
            'service': 'Web to Markdown Converter',
            'description': 'Convert web pages to Markdown format',
            'usage': {
                'endpoint': '/target',
                'method': 'GET',
                'parameters': {
                    'url': 'Target URL to convert (required)'
                },
                'example': '/target?url=https://example.com'
            },
            'response': {
                'content_type': 'text/plain',
                'encoding': 'utf-8'
            }
        }
        
        return jsonify(service_info)
        
    except Exception as e:
        logger.error(f"Index route failed: {str(e)}")
        return _create_error_response("Service information unavailable", 500)


async def _process_url_conversion(url: str) -> Dict[str, Any]:
    """
    处理 URL 转换的异步函数
    
    Args:
        url (str): 要转换的 URL
        
    Returns:
        Dict[str, Any]: 转换结果
    """
    try:
        # 使用渲染服务获取网页内容
        async with RendererService() as renderer:
            render_result = await renderer.render_page(url)
            
            if not render_result or not render_result.get('html'):
                return {
                    'success': False,
                    'error': 'Failed to render page content',
                    'status_code': 404
                }
            
            logger.info(f"Page rendered successfully: {url}")
            
            # 转换为 Markdown
            conversion_result = converter_service.convert_to_markdown(
                render_result['html'],
                render_result.get('final_url', url)
            )
            
            if not conversion_result or not conversion_result.get('markdown'):
                return {
                    'success': False,
                    'error': 'Failed to convert content to Markdown',
                    'status_code': 500
                }
            
            logger.info(f"Content converted to Markdown successfully: {url}")
            
            return {
                'success': True,
                'markdown': conversion_result['markdown'],
                'stats': conversion_result.get('stats', {}),
                'metadata': {
                    'original_url': url,
                    'final_url': render_result.get('final_url', url),
                    'title': render_result.get('title', ''),
                    'status_code': render_result.get('status_code', 200)
                }
            }
    
    except TimeoutError as e:
        logger.error(f"Timeout during conversion for {url}: {str(e)}")
        return {
            'success': False,
            'error': 'Request timeout - page took too long to load',
            'status_code': 408
        }
    
    except NetworkError as e:
        logger.error(f"Network error during conversion for {url}: {str(e)}")
        return {
            'success': False,
            'error': 'Network error - unable to access the URL',
            'status_code': 502
        }
    
    except RenderingError as e:
        logger.error(f"Rendering error for {url}: {str(e)}")
        return {
            'success': False,
            'error': 'Failed to render the webpage',
            'status_code': 500
        }
    
    except ConversionError as e:
        logger.error(f"Conversion error for {url}: {str(e)}")
        return {
            'success': False,
            'error': 'Failed to convert content to Markdown',
            'status_code': 500
        }
    
    except Exception as e:
        logger.error(f"Unexpected error during conversion for {url}: {str(e)}")
        return {
            'success': False,
            'error': 'An unexpected error occurred',
            'status_code': 500
        }


def _create_error_response(message: str, status_code: int) -> Response:
    """
    创建错误响应
    
    Args:
        message (str): 错误消息
        status_code (int): HTTP 状态码
        
    Returns:
        Response: 错误响应
    """
    error_info = {
        'error': True,
        'message': message,
        'status_code': status_code
    }
    
    return Response(
        response=str(error_info),
        status=status_code,
        mimetype='text/plain'
    )


@main_bp.errorhandler(WebToMarkdownError)
def handle_web_to_markdown_error(error: WebToMarkdownError) -> Response:
    """处理自定义异常"""
    logger.error(f"WebToMarkdownError: {error.message}")
    return _create_error_response(error.message, error.status_code)


@main_bp.errorhandler(404)
def handle_not_found(error) -> Response:
    """处理 404 错误"""
    return _create_error_response("Endpoint not found", 404)


@main_bp.errorhandler(405)
def handle_method_not_allowed(error) -> Response:
    """处理方法不允许错误"""
    return _create_error_response("Method not allowed", 405)


@main_bp.errorhandler(500)
def handle_internal_error(error) -> Response:
    """处理内部服务器错误"""
    logger.error(f"Internal server error: {str(error)}")
    return _create_error_response("Internal server error", 500)