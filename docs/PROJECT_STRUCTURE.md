# Web2MD 项目结构

## 目录概览

```
web2md/
├── app/                    # 应用主目录
│   ├── routes.py          # API 路由和 Bearer 认证
│   ├── services/          # 业务服务层
│   └── utils/             # 工具模块
├── config/                # 配置文件
├── test/                  # 测试文件
├── docs/                  # 文档目录
├── logs/                  # 日志目录
├── .env                   # 环境配置
├── requirements.txt       # Python 依赖
├── Dockerfile            # Docker 镜像
├── docker-compose.yml    # Docker Compose
├── setup.sh             # 安装脚本
├── run.py               # 启动入口
└── README.md            # 主文档
```

## 主要模块

- **routes.py**: API 端点、Bearer Token 鉴权
- **services/security.py**: URL 验证、黑名单过滤
- **services/renderer.py**: Playwright 网页渲染
- **services/converter.py**: HTML 到 Markdown 转换
- **config/settings.py**: 应用配置管理

## 文档

- **README.md**: 完整项目文档
- **QUICKSTART.md**: 5分钟快速开始指南
- **docs/AUTHENTICATION.md**: Bearer Token 详细指南
- **docs/IMPLEMENTATION_SUMMARY.md**: 功能实现总结
- **docs/PROJECT_STRUCTURE.md**: 本文件

## 测试

- **test/test_service.py**: 服务功能测试
- **test/test_authentication.py**: 认证功能测试
