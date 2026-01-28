#!/bin/bash

# Web2MD 服务安装脚本

set -e

echo "🚀 开始安装 Web to Markdown 服务..."

# 检查 Python 版本
echo "📋 检查 Python 版本..."
python3 --version

# 创建虚拟环境（可选）
if [ "$1" = "--venv" ]; then
    echo "🔧 创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ 虚拟环境已激活"
fi

# 安装 Python 依赖
echo "📦 安装 Python 依赖..."
pip install -r requirements.txt

# 安装 Playwright 浏览器
echo "🌐 安装 Playwright 浏览器..."
playwright install chromium

# 创建必要的目录
echo "📁 创建目录结构..."
mkdir -p logs

# 复制环境配置文件
if [ ! -f .env ]; then
    echo "⚙️ 创建环境配置文件..."
    cp .env.example .env
    
    # 生成随机 Bearer Token
    BEARER_TOKEN=$(python3 -c 'import secrets; print("Bearer-" + secrets.token_urlsafe(32))')
    echo "🔑 生成的 Bearer Token: $BEARER_TOKEN"
    
    # 更新 .env 文件中的 Bearer Token
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/BEARER_TOKEN=your-bearer-token-here/BEARER_TOKEN=$BEARER_TOKEN/" .env
    else
        # Linux
        sed -i "s/BEARER_TOKEN=your-bearer-token-here/BEARER_TOKEN=$BEARER_TOKEN/" .env
    fi
    
    echo "✅ Bearer Token 已写入 .env 文件"
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
    echo "ℹ️  .env 文件已存在"
    
    # 检查是否有 Bearer Token
    if ! grep -q "^BEARER_TOKEN=Bearer-" .env && ! grep -q "^BEARER_TOKEN=your-bearer-token-here" .env; then
        EXISTING_TOKEN=$(grep "^BEARER_TOKEN=" .env | cut -d'=' -f2)
        echo "ℹ️  现有的 Bearer Token: $EXISTING_TOKEN"
    elif grep -q "^BEARER_TOKEN=your-bearer-token-here" .env; then
        echo "⚠️  未检测到有效的 Bearer Token，正在生成..."
        BEARER_TOKEN=$(python3 -c 'import secrets; print("Bearer-" + secrets.token_urlsafe(32))')
        echo "🔑 生成的 Bearer Token: $BEARER_TOKEN"
        
        # 更新 .env 文件中的 Bearer Token
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' "s/^BEARER_TOKEN=.*/BEARER_TOKEN=$BEARER_TOKEN/" .env
        else
            # Linux
            sed -i "s/^BEARER_TOKEN=.*/BEARER_TOKEN=$BEARER_TOKEN/" .env
        fi
        
        echo "✅ Bearer Token 已更新到 .env 文件"
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
        EXISTING_TOKEN=$(grep "^BEARER_TOKEN=" .env | cut -d'=' -f2)
        echo "ℹ️  现有的 Bearer Token: $EXISTING_TOKEN"
    fi
fi

# 运行测试（可选）
if [ "$2" = "--test" ]; then
    echo "🧪 运行测试..."
    python -m pytest tests/ -v
fi

echo "✅ 安装完成！"
echo ""
echo "🎯 使用方法："
echo "  开发模式启动: python run.py"
echo "  运行测试:     python -m pytest tests/"
echo "  Docker 部署:  docker-compose up -d"
echo ""
echo "📖 更多信息请查看 README.md"