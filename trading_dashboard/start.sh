#!/bin/bash
# 交易监控仪表盘启动脚本

cd "$(dirname "$0")"

# 检查依赖
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📦 安装依赖..."
    pip3 install -r requirements.txt -q
fi

echo "🚀 启动交易监控仪表盘..."
echo "🌐 访问地址: http://localhost:8080"
echo "📊 API地址: http://localhost:8080/api/status"
echo "⏹️  按 Ctrl+C 停止"
echo ""

python3 app.py
