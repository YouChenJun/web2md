# 使用官方 Python 运行时作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 创建非 root 用户
RUN useradd --create-home --shell /bin/bash app

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 以 app 用户身份安装 Playwright 浏览器
USER app
RUN playwright install chromium
USER root
RUN playwright install-deps chromium

# 复制应用代码
COPY . .

# 创建日志目录
RUN mkdir -p logs && chown -R app:app /app

# 设置环境变量
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV PLAYWRIGHT_HEADLESS=True

# Web2MD - 暴露端口
EXPOSE 8080

USER app

# 启动命令
CMD ["python", "run.py"]