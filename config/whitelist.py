#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
域名白名单配置模块

定义允许访问的域名列表和域名验证规则。
"""

import re
from typing import List, Pattern


class DomainWhitelist:
    """域名白名单管理类"""
    
    def __init__(self):
        """初始化域名白名单"""
        self._allowed_domains: List[str] = [
            # 常见的安全域名
            'example.com',
            'httpbin.org',
            'jsonplaceholder.typicode.com',
            'github.com',
            'stackoverflow.com',
            'wikipedia.org',
            'mozilla.org',
            'w3.org',
            'ietf.org',
            "freebuf.com",
            # 可以根据需要添加更多域名
        ]
        
        self._allowed_patterns: List[Pattern] = [
            # 支持通配符匹配的域名模式
            re.compile(r'^.*\.github\.io$'),
            re.compile(r'^.*\.githubusercontent\.com$'),
            re.compile(r'^.*\.wikipedia\.org$'),
            re.compile(r'^.*\.freebuf\.com$'),
            # 可以根据需要添加更多模式
        ]
    
    def is_allowed(self, domain: str) -> bool:
        """
        检查域名是否在白名单中
        
        Args:
            domain (str): 要检查的域名
            
        Returns:
            bool: 如果域名被允许则返回 True，否则返回 False
        """
        if not domain:
            return False
        
        # 转换为小写进行比较
        domain = domain.lower()
        
        # 检查精确匹配
        if domain in self._allowed_domains:
            return True
        
        # 检查模式匹配
        for pattern in self._allowed_patterns:
            if pattern.match(domain):
                return True
        
        return False
    
    def add_domain(self, domain: str) -> None:
        """
        添加域名到白名单
        
        Args:
            domain (str): 要添加的域名
        """
        if domain and domain.lower() not in self._allowed_domains:
            self._allowed_domains.append(domain.lower())
    
    def remove_domain(self, domain: str) -> None:
        """
        从白名单中移除域名
        
        Args:
            domain (str): 要移除的域名
        """
        if domain:
            domain = domain.lower()
            if domain in self._allowed_domains:
                self._allowed_domains.remove(domain)
    
    def get_allowed_domains(self) -> List[str]:
        """
        获取所有允许的域名列表
        
        Returns:
            List[str]: 允许的域名列表
        """
        return self._allowed_domains.copy()


# 全局域名白名单实例
domain_whitelist = DomainWhitelist()