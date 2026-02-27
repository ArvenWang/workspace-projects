#!/bin/bash

# 交易监控面板启动脚本
# Trading Dashboard Startup Script

echo "🔥 启动币安合约交易监控面板..."
echo "================================"

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DASHBOARD_DIR="$HOME/.openclaw/workspace/trading_dashboard"

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python3"
    exit 1
fi

echo "✅ Python3 已安装"

# 创建虚拟环境（如果不存在）
if [ ! -d "$DASHBOARD_DIR/venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv "$DASHBOARD_DIR/venv"
fi

# 激活虚拟环境
source "$DASHBOARD_DIR/venv/bin/activate"

# 安装依赖
echo "📥 安装依赖..."
pip install -q -r "$DASHBOARD_DIR/requirements.txt"

# 检查端口是否被占用
PORT=8080
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  端口 $PORT 已被占用，尝试停止现有进程..."
    lsof -Pi :$PORT -sTCP:LISTEN -t | xargs kill -9 2>/dev/null
    sleep 1
fi

# 启动服务
echo "🚀 启动监控面板服务器..."
echo "📍 访问地址: http://localhost:$PORT"
echo "📊 按 Ctrl+C 停止服务器"
echo "================================"

cd "$DASHBOARD_DIR"
python3 app.py
