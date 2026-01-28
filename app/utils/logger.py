#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日志配置模块

配置应用的日志记录系统，包括文件日志、控制台日志和日志轮转。
"""

import os
import logging
import logging.handlers
from datetime import datetime
from typing import Optional

from config.settings import Config


def setup_logging(log_level: Optional[str] = None) -> None:
    """
    设置应用日志配置
    
    Args:
        log_level (Optional[str]): 日志级别，如果不指定则使用配置文件中的设置
    """
    config = Config()
    
    # 确定日志级别
    level = log_level or config.LOG_LEVEL
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # 创建日志目录
    log_dir = os.path.dirname(config.LOG_FILE) if os.path.dirname(config.LOG_FILE) else 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 清除现有的处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建格式化器
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 文件处理器（带轮转）
    file_handler = logging.handlers.RotatingFileHandler(
        filename=config.LOG_FILE,
        maxBytes=config.LOG_MAX_BYTES,
        backupCount=config.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # 错误日志处理器
    error_log_file = config.LOG_FILE.replace('.log', '_error.log')
    error_handler = logging.handlers.RotatingFileHandler(
        filename=error_log_file,
        maxBytes=config.LOG_MAX_BYTES,
        backupCount=config.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)
    
    # 设置第三方库的日志级别
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('playwright').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    
    logging.info(f"Logging system initialized with level: {level}")


class RequestLogger:
    """请求日志记录器"""
    
    def __init__(self):
        """初始化请求日志记录器"""
        self.logger = logging.getLogger('request')
    
    def log_request_start(self, url: str, client_ip: str, user_agent: str) -> str:
        """
        记录请求开始
        
        Args:
            url (str): 请求的 URL
            client_ip (str): 客户端 IP
            user_agent (str): 用户代理
            
        Returns:
            str: 请求 ID
        """
        request_id = self._generate_request_id()
        
        self.logger.info(
            f"REQUEST_START - ID: {request_id} | URL: {url} | "
            f"CLIENT_IP: {client_ip} | USER_AGENT: {user_agent}"
        )
        
        return request_id
    
    def log_request_end(self, request_id: str, status_code: int, 
                       processing_time: float, content_length: int = 0) -> None:
        """
        记录请求结束
        
        Args:
            request_id (str): 请求 ID
            status_code (int): HTTP 状态码
            processing_time (float): 处理时间（秒）
            content_length (int): 响应内容长度
        """
        self.logger.info(
            f"REQUEST_END - ID: {request_id} | STATUS: {status_code} | "
            f"TIME: {processing_time:.3f}s | SIZE: {content_length} bytes"
        )
    
    def log_request_error(self, request_id: str, error: str, error_type: str = "ERROR") -> None:
        """
        记录请求错误
        
        Args:
            request_id (str): 请求 ID
            error (str): 错误信息
            error_type (str): 错误类型
        """
        self.logger.error(
            f"REQUEST_ERROR - ID: {request_id} | TYPE: {error_type} | ERROR: {error}"
        )
    
    def _generate_request_id(self) -> str:
        """
        生成请求 ID
        
        Returns:
            str: 唯一的请求 ID
        """
        import uuid
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        short_uuid = str(uuid.uuid4())[:8]
        return f"{timestamp}-{short_uuid}"


class SecurityLogger:
    """安全事件日志记录器"""
    
    def __init__(self):
        """初始化安全日志记录器"""
        self.logger = logging.getLogger('security')
        
        # 创建安全日志文件处理器
        config = Config()
        security_log_file = config.LOG_FILE.replace('.log', '_security.log')
        
        security_handler = logging.handlers.RotatingFileHandler(
            filename=security_log_file,
            maxBytes=config.LOG_MAX_BYTES,
            backupCount=config.LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        
        security_formatter = logging.Formatter(
            fmt='%(asctime)s - SECURITY - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        security_handler.setFormatter(security_formatter)
        self.logger.addHandler(security_handler)
        self.logger.setLevel(logging.INFO)
    
    def log_url_validation_failed(self, url: str, reason: str, client_ip: str) -> None:
        """
        记录 URL 验证失败事件
        
        Args:
            url (str): 被拒绝的 URL
            reason (str): 拒绝原因
            client_ip (str): 客户端 IP
        """
        self.logger.warning(
            f"URL_VALIDATION_FAILED - URL: {url} | REASON: {reason} | CLIENT_IP: {client_ip}"
        )
    
    def log_threat_detected(self, url: str, threat_info: dict, client_ip: str) -> None:
        """
        记录威胁检测事件
        
        Args:
            url (str): 检测到威胁的 URL
            threat_info (dict): 威胁信息
            client_ip (str): 客户端 IP
        """
        self.logger.error(
            f"THREAT_DETECTED - URL: {url} | THREAT: {threat_info} | CLIENT_IP: {client_ip}"
        )
    
    def log_suspicious_activity(self, activity: str, details: dict, client_ip: str) -> None:
        """
        记录可疑活动
        
        Args:
            activity (str): 活动类型
            details (dict): 活动详情
            client_ip (str): 客户端 IP
        """
        self.logger.warning(
            f"SUSPICIOUS_ACTIVITY - TYPE: {activity} | DETAILS: {details} | CLIENT_IP: {client_ip}"
        )


class PerformanceLogger:
    """性能监控日志记录器"""
    
    def __init__(self):
        """初始化性能日志记录器"""
        self.logger = logging.getLogger('performance')
    
    def log_rendering_performance(self, url: str, render_time: float, 
                                content_size: int, success: bool) -> None:
        """
        记录渲染性能数据
        
        Args:
            url (str): 渲染的 URL
            render_time (float): 渲染时间（秒）
            content_size (int): 内容大小（字节）
            success (bool): 是否成功
        """
        status = "SUCCESS" if success else "FAILED"
        
        self.logger.info(
            f"RENDER_PERFORMANCE - URL: {url} | TIME: {render_time:.3f}s | "
            f"SIZE: {content_size} bytes | STATUS: {status}"
        )
    
    def log_conversion_performance(self, content_size: int, conversion_time: float,
                                 markdown_size: int, success: bool) -> None:
        """
        记录转换性能数据
        
        Args:
            content_size (int): 原始内容大小
            conversion_time (float): 转换时间（秒）
            markdown_size (int): Markdown 内容大小
            success (bool): 是否成功
        """
        status = "SUCCESS" if success else "FAILED"
        compression_ratio = markdown_size / content_size if content_size > 0 else 0
        
        self.logger.info(
            f"CONVERSION_PERFORMANCE - INPUT_SIZE: {content_size} bytes | "
            f"OUTPUT_SIZE: {markdown_size} bytes | TIME: {conversion_time:.3f}s | "
            f"COMPRESSION: {compression_ratio:.2f} | STATUS: {status}"
        )


# 全局日志记录器实例
request_logger = RequestLogger()
security_logger = SecurityLogger()
performance_logger = PerformanceLogger()