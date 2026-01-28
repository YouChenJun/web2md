#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
安全验证服务模块

提供 URL 安全验证功能，包括协议检查、域名白名单验证、威胁情报查询等。
"""

import re
import logging
from urllib.parse import urlparse
from typing import Dict, Any, Optional

from config.whitelist import domain_whitelist
from config.settings import Config
from app.utils.exceptions import URLValidationError, SecurityError


logger = logging.getLogger(__name__)


class SecurityService:
    """安全验证服务类"""
    
    def __init__(self):
        """初始化安全服务"""
        self.config = Config()
        self._ip_pattern = re.compile(
            r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
            r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        )
        self._private_ip_patterns = [
            re.compile(r'^10\.'),
            re.compile(r'^172\.(1[6-9]|2[0-9]|3[0-1])\.'),
            re.compile(r'^192\.168\.'),
            re.compile(r'^127\.'),
            re.compile(r'^0\.0\.0\.0$'),
        ]
    
    def validate_url(self, url: str) -> Dict[str, Any]:
        """
        验证 URL 的安全性
        
        Args:
            url (str): 要验证的 URL
            
        Returns:
            Dict[str, Any]: 验证结果，包含是否安全、错误信息等
            
        Raises:
            URLValidationError: URL 格式无效
            SecurityError: 安全验证失败
        """
        if not url or not isinstance(url, str):
            raise URLValidationError("URL cannot be empty")
        
        # 基础格式验证
        try:
            parsed_url = urlparse(url.strip())
        except Exception as e:
            logger.error(f"URL parsing failed: {url}, error: {str(e)}")
            raise URLValidationError(f"Invalid URL format: {str(e)}")
        
        # 协议检查
        if not self._check_protocol(parsed_url.scheme):
            raise SecurityError(f"Protocol '{parsed_url.scheme}' is not allowed")
        
        # 域名/IP 检查
        hostname = parsed_url.hostname
        if not hostname:
            raise URLValidationError("URL must contain a valid hostname")
        
        # 检查是否为 IP 地址
        if self._is_ip_address(hostname):
            if self._is_private_ip(hostname):
                raise SecurityError(f"Private IP address not allowed: {hostname}")
        else:
            # 域名黑名单检查
            # 注释：已禁用白名单验证，仅保留黑名单功能
            # if not domain_whitelist.is_allowed(hostname):
            #     raise SecurityError(f"Domain not in whitelist: {hostname}")
            logger.debug(f"Domain whitelist check disabled for: {hostname}")
            
            # 黑名单检查
            if self._is_domain_blocked(hostname):
                raise SecurityError(f"Domain is in blacklist: {hostname}")
        
        # 威胁情报检查
        threat_result = self._check_threat_intelligence(url)
        
        return {
            'is_safe': True,
            'url': url,
            'hostname': hostname,
            'protocol': parsed_url.scheme,
            'threat_info': threat_result
        }
    
    def _check_protocol(self, protocol: str) -> bool:
        """
        检查协议是否允许
        
        Args:
            protocol (str): URL 协议
            
        Returns:
            bool: 协议是否被允许
        """
        if not protocol:
            return False
        
        return protocol.lower() in self.config.ALLOWED_PROTOCOLS
    
    def _is_ip_address(self, hostname: str) -> bool:
        """
        检查是否为 IP 地址
        
        Args:
            hostname (str): 主机名
            
        Returns:
            bool: 是否为 IP 地址
        """
        return self._ip_pattern.match(hostname) is not None
    
    def _is_domain_blocked(self, domain: str) -> bool:
        """
        检查域名是否在黑名单中
        
        Args:
            domain (str): 域名
            
        Returns:
            bool: 是否在黑名单中
        """
        try:
            blocked_domains = self.config.BLOCKED_DOMAINS
            domain_lower = domain.lower()
            
            # 精确匹配
            if domain_lower in blocked_domains:
                return True
            
            # 通配符匹配
            for blocked_pattern in blocked_domains:
                if '*' in blocked_pattern:
                    # 转换为正则表达式
                    pattern = blocked_pattern.replace('.', r'\.').replace('*', '.*')
                    import re
                    if re.match(f'^{pattern}$', domain_lower):
                        return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Blacklist check failed for {domain}: {str(e)}")
            return False
    
    def _is_private_ip(self, ip: str) -> bool:
        """
        检查是否为私有 IP 地址
        
        Args:
            ip (str): IP 地址
            
        Returns:
            bool: 是否为私有 IP
        """
        for pattern in self._private_ip_patterns:
            if pattern.match(ip):
                return True
        return False
    
    def _check_threat_intelligence(self, url: str) -> Optional[Dict[str, Any]]:
        """
        使用威胁情报服务检查 URL 安全性
        
        Args:
            url (str): 要检查的 URL
            
        Returns:
            Optional[Dict[str, Any]]: 威胁情报结果，如果检查失败则返回 None
        """
        try:
            logger.info(f"Checking threat intelligence for URL: {url}")
            
            # 使用 ti-query-mcp 服务进行威胁情报查询
            from app.services.threat_intel import ThreatIntelService
            
            threat_service = ThreatIntelService()
            result = threat_service.analyze_url(url)
            
            if result and result.get('threat_level') == 'malicious':
                raise SecurityError(f"URL identified as malicious: {url}")
            
            return result
            
        except SecurityError:
            # 重新抛出安全错误
            raise
        except Exception as e:
            logger.warning(f"Threat intelligence check failed for {url}: {str(e)}")
            # 威胁情报检查失败时，不阻止请求，但记录警告
            return None
    
    def check_domain_reputation(self, domain: str) -> Dict[str, Any]:
        """
        检查域名声誉
        
        Args:
            domain (str): 域名
            
        Returns:
            Dict[str, Any]: 域名声誉信息
        """
        try:
            logger.info(f"Checking domain reputation: {domain}")
            
            # TODO: 实现域名声誉检查逻辑
            # 可以集成多个威胁情报源
            
            return {
                'domain': domain,
                'reputation': 'good',
                'risk_score': 0.1,
                'last_checked': None
            }
            
        except Exception as e:
            logger.error(f"Domain reputation check failed for {domain}: {str(e)}")
            return {
                'domain': domain,
                'reputation': 'unknown',
                'risk_score': 0.5,
                'error': str(e)
            }