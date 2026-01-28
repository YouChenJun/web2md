# Web2MD - Bearer Token 认证指南

## 概述

Web2MD 服务使用 Bearer Token 进行身份验证。所有 `/target` 请求都必须包含有效的认证令牌。

## 快速开始

### 1. 获取 Token

#### 方式 A：使用 setup.sh 自动生成（推荐）

```bash
./setup.sh --venv
```

脚本会自动生成 Bearer Token 并保存到 `.env` 文件，同时输出 token 信息。

#### 方式 B：手动生成

```bash
# 生成随机 Token
python3 -c 'import secrets; print(secrets.token_urlsafe(32))'
```

#### 方式 C：Docker 部署

```bash
./docker-start.sh
```

脚本会自动生成 Token、保存到 `.docker.env` 并输出到控制台。

### 2. 配置 Token

将生成的 token 添加到 `.env` 文件：

```bash
BEARER_TOKEN=your-generated-token-here
ENABLE_BEARER_AUTH=True
```

### 3. 使用 Token

在请求头中添加 `Authorization`：

```bash
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     "http://localhost:8080/target?url=https://example.com"
```

## API 使用示例

### 成功请求

```bash
curl -H "Authorization: Bearer mimFfgEGls8fZRjsTjeeQXC7DBiUbhTNHam-sIx9j5M" \
     "http://localhost:8080/target?url=https://httpbin.org/html"
```

**响应：**
```
# 网页标题

网页内容...
```

### 失败请求

#### 缺少认证

```bash
curl "http://localhost:8080/target?url=https://example.com"
```

**响应：**
```json
{
  "error": true,
  "message": "Missing Authorization header",
  "status_code": 401
}
```

#### Token 无效

```bash
curl -H "Authorization: Bearer wrong-token" \
     "http://localhost:8080/target?url=https://example.com"
```

**响应：**
```json
{
  "error": true,
  "message": "Invalid or expired Bearer token",
  "status_code": 401
}
```

#### 格式错误

```bash
curl -H "Authorization: InvalidFormat" \
     "http://localhost:8080/target?url=https://example.com"
```

**响应：**
```json
{
  "error": true,
  "message": "Invalid Authorization header format. Expected: 'Bearer <token>'",
  "status_code": 401
}
```

## 安全配置

### 禁用认证（仅开发环境）

如需临时禁用认证，修改 `.env` 文件：

```bash
ENABLE_BEARER_AUTH=False
```

⚠️ **警告**：生产环境必须启用认证！

### 黑名单（已启用）

默认黑名单包括：
- `localhost`
- `127.0.0.1`
- `::1`
- 私有 IP：`10.x.x.x`, `172.16.x.x` - `172.31.x.x`, `192.168.x.x`

在 `config/settings.py` 的 `BLOCKED_DOMAINS` 中配置。

### 白名单（已禁用）

⚠️ **重要**：白名单验证已被注释，仅保留黑名单功能。

当前行为：
- ✅ 任何不在黑名单中的域名都可以访问
- ❌ 黑名单中的域名/IP 会被拒绝

**如何重新启用白名单：**

1. 编辑 `app/services/security.py`，取消注释第 79-81 行：
```python
# 域名白名单检查
if not domain_whitelist.is_allowed(hostname):
    raise SecurityError(f"Domain not in whitelist: {hostname}")
```

2. 编辑 `config/whitelist.py`，添加允许的域名：
```python
self._allowed_domains: List[str] = [
    'example.com',
    'github.com',
    # 添加您的域名
]
```

## Docker 部署

### 自动启动（推荐）

```bash
./docker-start.sh
```

脚本会自动：
1. 生成随机 Bearer Token
2. 保存到 `.docker.env`
3. 输出 Token 信息
4. 启动服务

**输出示例：**
```
🔑 您的 Bearer Token（请妥善保存）:
   Bearer-Hr8wkWI_RSdi9X8uYsjtXqN_cQu7KM90g7EwbyAK6OE
═══════════════════════════════════════════════════════════
📝 使用方法:
   curl -H "Authorization: Bearer Bearer-Hr8wkWI_RSdi9X8uYsjtXqN_cQu7KM90g7EwbyAK6OE" \
        "http://localhost:8080/target?url=https://example.com"
```

### 手动启动

```bash
# 1. 生成 Token
python3 -c 'import secrets; print("Bearer-" + secrets.token_urlsafe(32))' > .docker.env

# 2. 查看生成的 Token
cat .docker.env

# 3. 启动服务
docker-compose up -d
```

### 查看 Token

```bash
cat .docker.env
# 输出：BEARER_TOKEN=Bearer-xxx...
```

## 环境变量说明

### .env 文件

```bash
# Flask 应用配置
FLASK_ENV=development              # 运行环境
FLASK_DEBUG=True                   # 调试模式
FLASK_HOST=0.0.0.0              # 监听地址
FLASK_PORT=8080                   # 服务端口

# 安全配置
SECRET_KEY=your-secret-key          # Flask 密钥
BEARER_TOKEN=your-token           # Bearer Token（必需）
ENABLE_BEARER_AUTH=True          # 是否启用 Token 认证

# Playwright 配置
PLAYWRIGHT_TIMEOUT=30000         # 超时时间（毫秒）
PLAYWRIGHT_HEADLESS=True          # 无头模式

# 日志配置
LOG_LEVEL=INFO                   # 日志级别
LOG_FILE=logs/app.log           # 日志文件路径
LOG_MAX_BYTES=10485760          # 单个日志文件最大大小（10MB）
LOG_BACKUP_COUNT=5              # 保留的历史日志文件数量

# 安全配置
MAX_CONTENT_LENGTH=16777216       # 最大请求内容长度（16MB）
```

### .docker.env 文件（Docker 专用）

```bash
# Bearer Token（Docker Compose 使用）
BEARER_TOKEN=Bearer-xxx...
```

## 故障排除

### 问题：认证失败

**症状**：
```json
{
  "error": true,
  "message": "Invalid or expired Bearer token",
  "status_code": 401
}
```

**解决方案**：
1. 检查 `.env` 文件中的 `BEARER_TOKEN` 是否正确
2. 确认使用的是 `Bearer <token>` 格式（注意有空格）
3. 重启服务使配置生效

### 问题：提示未配置认证

**症状**：
```json
{
  "error": true,
  "message": "Authentication is required but not configured",
  "status_code": 500
}
```

**解决方案**：
1. 在 `.env` 文件中添加 `BEARER_TOKEN`
2. 确保 `ENABLE_BEARER_AUTH=True`
3. 重启服务

### 问题：Docker 启动失败

**症状**：服务无法启动，日志显示认证相关错误

**解决方案**：
```bash
# 重新生成 Token
python3 -c 'import secrets; print("Bearer-" + secrets.token_urlsafe(32))' > .docker.env

# 重新启动
docker-compose down
docker-compose up -d
```

## 最佳实践

### Token 管理

1. **安全性**
   - ✅ 使用强随机 Token（32+ 字符）
   - ✅ 定期更换 Token
   - ❌ 不要将 Token 提交到版本控制
   - ❌ 不要在日志中输出完整 Token

2. **存储**
   - ✅ 使用环境变量存储
   - ✅ 将 `.env` 添加到 `.gitignore`
   - ❌ 不要硬编码在代码中

3. **使用**
   - ✅ 使用 HTTPS 传输
   - ✅ 定期审计 Token 使用情况
   - ❌ 不要在 URL 参数中传递

### 生产环境部署

1. 确保启用 Bearer 认证
2. 使用强密钥和 Token
3. 配置日志级别为 WARNING 或 ERROR
4. 启用黑名单和白名单（如需要）
5. 定期审查安全日志

## 测试验证

### 测试脚本

```bash
#!/bin/bash

TOKEN="your-token-here"
BASE_URL="http://localhost:8080"

echo "=== 测试 1: 不带 Token（应该失败）==="
curl -s "$BASE_URL/target?url=https://example.com"
echo ""

echo "=== 测试 2: 带错误 Token（应该失败）==="
curl -s -H "Authorization: Bearer wrong-token" \
     "$BASE_URL/target?url=https://example.com"
echo ""

echo "=== 测试 3: 带正确 Token（应该成功）==="
curl -s -H "Authorization: Bearer $TOKEN" \
     "$BASE_URL/target?url=https://httpbin.org/html" | head -5
echo ""

echo "=== 测试 4: 健康检查（无需认证）==="
curl -s "$BASE_URL/health"
echo ""
```

## 参考链接

- [RFC 6750 - OAuth 2.0 Bearer Token Usage](https://tools.ietf.org/html/rfc6750)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Playwright Documentation](https://playwright.dev/)
