# Web2MD

<div align="center">

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1+-green.svg)
![Playwright](https://img.shields.io/badge/Playwright-1.57+-red.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

**Web2MD** - 基于 Flask 的网页到 Markdown 转换服务

使用 Playwright + Chromium 渲染动态网页，智能提取内容并转换为 Markdown 格式。

</div>

---

## 🎯 什么是 Web2MD？

**Web2MD** 是一个强大的网页内容提取和转换服务，可以将任何网页 URL 转换为干净的 Markdown 格式文本。

### 核心功能

- 🌐 **完整网页渲染**：使用 Playwright + Chromium 处理 JavaScript 动态内容
- 📝 **智能内容提取**：自动识别主要内容区域，过滤导航和广告
- 🔒 **安全验证**：Bearer Token 认证、URL 协议检查、黑名单过滤
- ⚡ **高性能转换**：优化的 HTML 到 Markdown 转换算法
- 📊 **详细日志**：完整的请求日志、错误日志和性能监控
- 🛡️ **错误处理**：全面的异常处理和用户友好的错误响应
- 🐳 **Docker 支持**：提供完整的容器化部署方案

### 使用场景

#### 🤖 AI 应用集成

**让 AI 理解网页内容**
- LLM 应用需要获取和分析网页内容时，提供干净的结构化文本
- RAG 系统中，将网页知识转换为 Markdown 便于向量化和检索
- AI Agent 需要读取网页信息时，提供纯文本格式减少 Token 消耗

**典型工作流：**
```
网页 URL → Web2MD → Markdown → AI 处理 → 结构化输出
```

#### 📚 内容管理与归档

- 将在线文章、博客转换为 Markdown 便于本地保存
- 技术文档自动归档和版本管理
- 知识库系统的内容抓取和整理

#### 📊 数据采集与分析

- 批量网页内容提取和分析
- 竞品监控和价格比较
- 新闻和舆情监控

#### 🔗 API 集成示例

**AI 应用调用示例：**
```python
import requests

# 获取网页的 Markdown 内容
response = requests.get(
    "http://localhost:9097/target",
    params={"url": "https://example.com/article"},
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

markdown_content = response.text

# 直接喂给 AI
# ai_response = openai.ChatCompletion.create(
#     messages=[{"role": "user", "content": markdown_content}]
# )
```

---

## 🚀 快速开始

### 方式 1：自动安装（推荐）

```bash
# 克隆项目
git clone https://github.com/yourusername/web2md.git
cd web2md

# 运行安装脚本（自动生成 Bearer Token）
./setup.sh --venv

# 启动服务
python run.py
```

### 方式 2：手动安装

```bash
# 1. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 安装浏览器
playwright install chromium

# 4. 配置环境
cp .env.example .env
vim .env  # 编辑配置文件

# 5. 启动服务
python run.py
```

### 方式 3：Docker 部署

```bash
# 自动启动（推荐）
./docker-start.sh

# 或手动启动
docker-compose up -d
```

---

## 📡 API 使用

### 认证

所有 `/target` 请求都需要 **Bearer Token** 认证。

#### 获取 Token

```bash
# 方式 1：查看 .env 文件
grep BEARER_TOKEN .env

# 方式 2：使用 setup.sh 生成
./setup.sh --venv
```

#### 使用格式

```http
Authorization: Bearer YOUR_TOKEN_HERE
```

### 转换网页为 Markdown

```http
GET /target?url=https://example.com
```

**参数：**
- `url` (必需): 要转换的目标网页 URL

**响应：**
- 成功：返回 Markdown 格式的内容 (Content-Type: `text/plain`)
- 失败：返回错误信息和相应的 HTTP 状态码

**示例：**

```bash
# 转换示例网页
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:9097/target?url=https://httpbin.org/html"

# 转换 GitHub README
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:9097/target?url=https://github.com/microsoft/playwright"
```

### 健康检查

```http
GET /health
```

**示例：**

```bash
curl http://localhost:9097/health
```

**响应：**

```json
{
  "service": "web-to-markdown",
  "status": "healthy",
  "version": "1.0.0",
  "endpoints": {
    "/health": "Health check",
    "/target": "Convert URL to Markdown"
  }
}
```

### 服务信息

```http
GET /
```

返回 API 使用说明和服务信息。

---

## 🔒 安全配置

### Bearer Token 认证

**状态**：已启用

Web2MD 使用 Bearer Token 进行身份验证，确保只有授权用户才能访问转换服务。

**配置：**

```bash
# .env 文件
BEARER_TOKEN=your-generated-token
ENABLE_BEARER_AUTH=True
```

**错误码：**

| 状态码 | 说明 |
|---------|------|
| 401 | 缺少或无效的 Token |
| 403 | 访问被拒绝（黑名单等） |

详细说明请参考 [docs/AUTHENTICATION.md](docs/AUTHENTICATION.md)。

### URL 黑名单

**状态**：已启用

默认黑名单包括：
- `localhost`
- `127.0.0.1`
- `::1`
- 私有 IP 范围（10.x.x.x, 172.16-31.x.x, 192.168.x.x）

在 `config/settings.py` 的 `BLOCKED_DOMAINS` 中配置。

### URL 白名单

**状态**：已禁用

白名单验证已被注释，仅黑名单生效。任何不在黑名单中的域名都可以访问。

如需重新启用，请参考 [docs/IMPLEMENTATION_SUMMARY.md](docs/IMPLEMENTATION_SUMMARY.md)。

### 安全设置

- **允许的协议**：仅支持 `http` 和 `https`
- **阻止的地址**：本地地址、内网 IP 等
- **请求超时**：30 秒页面加载超时
- **内容大小限制**：最大 16MB 响应内容

---

## ⚙️ 配置选项

### 环境变量

| 变量名 | 默认值 | 说明 |
|---------|---------|------|
| `FLASK_ENV` | `development` | 运行环境：development / production |
| `FLASK_DEBUG` | `True` | 调试模式 |
| `FLASK_HOST` | `0.0.0.0` | 服务监听地址 |
| `FLASK_PORT` | `8080` | 服务端口 |
| `SECRET_KEY` | - | Flask 加密密钥（必需） |
| `BEARER_TOKEN` | - | Bearer Token（必需） |
| `ENABLE_BEARER_AUTH` | `True` | 是否启用 Token 认证 |
| `PLAYWRIGHT_TIMEOUT` | `30000` | 页面加载超时（毫秒） |
| `PLAYWRIGHT_HEADLESS` | `True` | 无头浏览器模式 |
| `LOG_LEVEL` | `INFO` | 日志级别 |
| `LOG_FILE` | `logs/app.log` | 日志文件路径 |
| `LOG_MAX_BYTES` | `10485760` | 单个日志文件最大大小（10MB） |
| `LOG_BACKUP_COUNT` | `5` | 保留的历史日志文件数量 |
| `MAX_CONTENT_LENGTH` | `16777216` | 最大请求内容长度（16MB） |

---

## 📊 日志系统

Web2MD 提供多种类型的日志：

- **应用日志** (`logs/app.log`): 一般应用事件
- **错误日志** (`logs/app_error.log`): 错误和异常
- **安全日志** (`logs/app_security.log`): 安全相关事件
- **服务器日志** (`logs/server.log`): 服务器启动和请求日志

### 查看日志

```bash
# 实时查看日志
tail -f logs/server.log

# 查看错误日志
tail -f logs/app_error.log
```

---

## 🧪 测试

### 运行测试

```bash
# 进入项目目录
cd web2md

# 激活虚拟环境
source venv/bin/activate

# 运行认证测试
python test/test_authentication.py YOUR_TOKEN

# 运行功能测试
python test/test_service.py
```

### 测试覆盖

- ✅ Bearer Token 认证
- ✅ URL 验证
- ✅ 黑名单过滤
- ✅ 网页渲染
- ✅ Markdown 转换
- ✅ 错误处理

详细测试说明请参考 [test/](test/) 目录。

---

## 📂 项目结构

```
web2md/
├── app/                    # 应用主目录
│   ├── __init__.py        # Flask 应用初始化
│   ├── routes.py          # API 路由定义
│   ├── services/          # 业务服务层
│   │   ├── security.py    # 安全验证服务
│   │   ├── renderer.py    # 网页渲染服务
│   │   ├── converter.py   # Markdown 转换服务
│   │   └── threat_intel.py # 威胁情报服务
│   └── utils/             # 工具模块
│       ├── logger.py      # 日志配置
│       └── exceptions.py  # 自定义异常
├── config/                # 配置文件
│   ├── settings.py        # 应用配置
│   └── whitelist.py       # 域名白名单（已禁用）
├── test/                  # 测试文件
│   ├── test_service.py          # 服务功能测试
│   └── test_authentication.py  # 认证功能测试
├── docs/                  # 文档目录
│   ├── AUTHENTICATION.md          # 认证详细指南
│   └── IMPLEMENTATION_SUMMARY.md # 功能实现总结
├── logs/                  # 日志目录
│   ├── app.log           # 应用日志
│   ├── app_error.log     # 错误日志
│   ├── app_security.log  # 安全日志
│   └── server.log        # 服务器日志
├── .env                   # 环境配置（不提交到 Git）
├── .env.example           # 环境配置模板
├── .gitignore            # Git 忽略文件
├── requirements.txt       # Python 依赖
├── Dockerfile            # Docker 镜像构建
├── docker-compose.yml    # Docker Compose 配置
├── docker-start.sh       # Docker 自动启动脚本
├── setup.sh             # 安装和配置脚本
├── run.py               # 应用启动入口
└── README.md            # 项目文档
```

---

## 🐳 Docker 部署

### 快速部署

```bash
# 1. 构建镜像
docker-compose build

# 2. 启动服务
./docker-start.sh
```

### 手动部署

```bash
# 1. 生成 Token
python3 -c 'import secrets; print("Bearer-" + secrets.token_urlsafe(32))' > .docker.env

# 2. 启动服务
docker-compose up -d

# 3. 查看日志
docker-compose logs -f

# 4. 停止服务
docker-compose down
```

### Docker Compose 配置

```yaml
version: '3.8'

services:
  web2md:
    build: .
    ports:
      - "9097:8080"
    environment:
      - BEARER_TOKEN=${BEARER_TOKEN}
      - ENABLE_BEARER_AUTH=True
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
```

---

## 📈 性能优化

### 浏览器优化

- ✅ 使用无头模式减少资源占用
- ✅ 优化 Chromium 启动参数
- ✅ 实现浏览器实例复用

### 内容处理优化

- ✅ 智能提取主要内容区域
- ✅ 过滤无关元素（导航、广告等）
- ✅ 优化图片链接处理
- ✅ 减少 DOM 操作次数

---

## 🏭 生产环境建议

### 1. 使用生产级 WSGI 服务器

```bash
pip install gunicorn

# 启动服务
gunicorn -w 4 -b 0.0.0.0:8080 run:app
```

### 2. 配置反向代理

**Nginx 配置示例：**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. 安全配置

```bash
# 禁用调试模式
FLASK_DEBUG=False

# 使用强密钥
SECRET_KEY=<generated-with-secrets>
BEARER_TOKEN=<generated-with-secrets>

# 设置适当的日志级别
LOG_LEVEL=WARNING
```

### 4. 监控和日志

- 配置日志轮转
- 设置日志监控系统（如 ELK、Graylog）
- 监控服务器资源使用
- 设置告警规则

---

## 🔧 开发指南

### 添加新功能

1. 在相应的服务模块中实现业务逻辑
2. 在 `app/routes.py` 中添加 API 端点
3. 更新配置文件和文档
4. 添加相应的错误处理和日志记录
5. 在 `test/` 目录添加测试

### 代码风格

项目遵循 Python PEP8 编码规范：

```bash
# 检查代码风格
flake8 app/

# 自动格式化
black app/
```

---

## ❓ 故障排除

### 常见问题

#### 1. Playwright 安装失败

```bash
# 手动安装浏览器
playwright install chromium

# 或安装所有浏览器
playwright install --with-deps
```

#### 2. Token 认证失败

```bash
# 检查配置
grep BEARER_TOKEN .env

# 重启服务
pkill -f "python run.py"
python run.py
```

#### 3. 端口被占用

```bash
# 查找占用端口的进程
lsof -ti:9097

# 修改端口
export FLASK_PORT=8081
python run.py
```

#### 4. 权限错误

```bash
# 确保日志目录有写权限
mkdir -p logs
chmod 755 logs
```

#### 5. 内存不足

- 减少并发请求数量
- 优化浏览器参数
- 增加系统内存
- 使用无头模式

---

## 📖 文档

- **[docs/AUTHENTICATION.md](docs/AUTHENTICATION.md)** - Bearer Token 认证详细指南
- **[docs/IMPLEMENTATION_SUMMARY.md](docs/IMPLEMENTATION_SUMMARY.md)** - 功能实现总结

---

## 📝 更新日志

### 版本 1.0.0 (2026-01-28)

- ✅ 初始版本发布
- ✅ Bearer Token 认证
- ✅ Playwright 网页渲染
- ✅ 智能内容提取
- ✅ Markdown 转换
- ✅ 黑名单过滤
- ✅ Docker 支持
- ✅ 完整日志系统
- ✅ 自动化测试套件

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 👨‍💻 项目起源

> **"Pure Vibe Coding with AI"** 🚀

本项目由 **GLM (智谱清言)** + **Claude Code** 协作生成，全程采用 AI 辅助编程（Vibe Coding）模式。

### 技术栈

- **AI 助手**：GLM-4 + Claude Sonnet 4.5
- **开发模式**：Natural Language → Code
- **代码质量**：AI 生成，人工审查

### AI 辅助开发流程

1. **需求定义**：自然语言描述功能需求
2. **架构设计**：AI 辅助设计项目结构
3. **代码生成**：AI 生成核心代码
4. **测试验证**：自动化测试 + 人工验证
5. **文档编写**：AI 生成完整文档

这种开发方式证明了 AI 辅助编程的可行性和效率，展示了未来软件开发的新模式。

---

---

## 🙏 致谢

感谢以下开源项目：

- [Flask](https://flask.palletsprojects.com/)
- [Playwright](https://playwright.dev/)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- [markdownify](https://github.com/matthewwithanm/markdownify)

---

<div align="center">

**如果这个项目对您有帮助，请给个 ⭐️**

Made with ❤️ & 🤖 by GLM + Claude Code (Pure Vibe Coding)

</div>
