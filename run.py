#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Flask 应用启动入口

该模块负责启动 Flask Web 服务。
"""

import os
from app import create_app
from config.settings import config


def main():
    """主函数，启动 Flask 应用"""
    # 获取环境配置
    config_name = os.environ.get('FLASK_ENV', 'default')
    app_config = config.get(config_name, config['default'])
    
    # 创建应用实例
    app = create_app()
    app.config.from_object(app_config)
    
    # 启动应用
    app.run(
        host=app_config.HOST,
        port=app_config.PORT,
        debug=app_config.DEBUG
    )


if __name__ == '__main__':
    main()