#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Flask Web 应用初始化模块

该模块负责创建和配置 Flask 应用实例，注册路由和中间件。
"""

from flask import Flask

from app.routes import main_bp
from app.utils.logger import setup_logging


def create_app():
    """
    创建 Flask 应用实例
    
    Returns:
        Flask: 配置完成的 Flask 应用实例
    """
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object('config.settings')
    
    # 设置日志
    setup_logging()
    
    # 注册蓝图
    app.register_blueprint(main_bp)
    
    return app