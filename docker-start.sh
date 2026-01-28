#!/bin/bash

# Web2MD - Docker Compose 启动脚本

set -e

echo "🚀 开始使用 Docker Compose 启动 Web2MD 服务..."

# 生成随机 Bearer Token
if [ ! -f .docker.env ] || [ -z "$BEARER_TOKEN" ]; then
    echo "🔑 生成随机 Bearer Token..."
    BEARER_TOKEN=$(python3 -c 'import secrets; print("Bearer-" + secrets.token_urlsafe(32))' 2>/dev/null || openssl rand -base64 32 | tr -d '/+=' | head -c 32)
    
    # 保存到 .docker.env
    cat > .docker.env <<EOF
BEARER_TOKEN=$BEARER_TOKEN
EOF
    
    echo "✅ Bearer Token 已生成并保存到 .docker.env"
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "🔑 您的 Bearer Token（请妥善保存）:"
    echo "   $BEARER_TOKEN"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "📝 使用方法:"
    echo "   curl -H \"Authorization: Bearer $BEARER_TOKEN\" \\"
    echo "        \"http://localhost:8080/target?url=https://example.com\""
    echo ""
else
    echo "ℹ️  使用现有的 Bearer Token"
    source .docker.env
    echo "   Bearer Token: $BEARER_TOKEN"
fi

# 创建日志目录
mkdir -p logs

# 启动服务
echo "🐳 启动 Docker Compose 服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "✅ 服务启动成功！"
    echo ""
    echo "📡 服务地址:"
    echo "   http://localhost:8080"
    echo ""
    echo "🔍 健康检查:"
    echo "   curl http://localhost:8080/health"
    echo ""
    echo "📖 查看日志:"
    echo "   docker-compose logs -f"
    echo ""
    echo "🛑 停止服务:"
    echo "   docker-compose down"
    echo ""
else
    echo "❌ 服务启动失败，请查看日志:"
    echo "   docker-compose logs"
    exit 1
fi
