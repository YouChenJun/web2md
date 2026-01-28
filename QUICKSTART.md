# Web2MD 快速开始指南

## 5分钟快速启动 Web2MD

### 1. 安装和配置

```bash
# 克隆或进入项目目录
cd web2md

# 运行安装脚本（自动生成 Bearer Token）
./setup.sh --venv
```

**输出示例：**
```
🔑 生成的 Bearer Token: Bearer-AbCdEfGhIjKlMnOpQrStUvWxYz

═══════════════════════════════════════════════════════
🔑 您的 Bearer Token（请妥善保存）:
   Bearer-AbCdEfGhIjKlMnOpQrStUvWxYz
═══════════════════════════════════════════════════════

📝 使用方法:
   curl -H "Authorization: Bearer Bearer-AbCdEfGhIjKlMnOpQrStUvWxYz" \
        "http://localhost:8080/target?url=https://example.com"
```

### 2. 启动服务

```bash
# 激活虚拟环境并启动
source venv/bin/activate && python run.py
```

服务将在 `http://localhost:8080` 启动。

### 3. 测试服务

#### 健康检查（无需认证）

```bash
curl http://localhost:8080/health
```

#### 转换网页（需要认证）

```bash
# 将您的 Token 替换到下方命令
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     "http://localhost:8080/target?url=https://httpbin.org/html"
```

## Docker 部署（1分钟）

```bash
# 运行 Docker 自动启动脚本
./docker-start.sh

# 查看服务日志
docker-compose logs -f web2md
```

## 常用命令

### 查看日志

```bash
# 服务器日志
tail -f logs/server.log

# 应用日志
tail -f logs/app.log
```

### 重启服务

```bash
# 停止服务
pkill -f "python run.py"

# 启动服务
source venv/bin/activate && python run.py
```

### 测试认证

```bash
# 运行自动化测试
source venv/bin/activate
python test/test_authentication.py YOUR_TOKEN
```

## 环境配置

### .env 文件

```bash
# Flask 配置
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=8080

# 安全配置
SECRET_KEY=your-secret-key
BEARER_TOKEN=your-generated-token
ENABLE_BEARER_AUTH=True

# Playwright 配置
PLAYWRIGHT_TIMEOUT=30000
PLAYWRIGHT_HEADLESS=True

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

## 故障排除

### 问题：端口被占用

```bash
# 修改端口
export FLASK_PORT=8081
python run.py
```

### 问题：认证失败

```bash
# 检查 Token
grep BEARER_TOKEN .env

# 重新生成 Token
./setup.sh --venv
```

### 问题：服务无法启动

```bash
# 查看详细日志
python run.py --debug

# 或查看日志文件
tail -50 logs/server.log
```

## 下一步

1. 阅读完整文档：[README.md](README.md)
2. 了解认证机制：[docs/AUTHENTICATION.md](docs/AUTHENTICATION.md)
3. 查看功能实现：[docs/IMPLEMENTATION_SUMMARY.md](docs/IMPLEMENTATION_SUMMARY.md)
4. 运行测试套件：[test/](test/)

## 支持

- 📖 [完整文档](README.md)
- 🔐 [认证指南](docs/AUTHENTICATION.md)
- 🧪 [测试文件](test/)
- 📊 [实现总结](docs/IMPLEMENTATION_SUMMARY.md)

---

**祝您使用愉快！** 🎉
