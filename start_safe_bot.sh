#!/bin/bash
# 🛡️ 启动稳健交易机器人 v2.0

echo "=========================================="
echo "🛡️ 稳健盈利交易机器人 v2.0"
echo "=========================================="
echo ""

# 检查Python
echo "📋 检查环境..."
python3 --version || { echo "❌ Python3 未安装"; exit 1; }

# 检查依赖
echo "📦 检查依赖..."
pip3 show cryptography requests > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "⚠️  安装依赖..."
    pip3 install cryptography requests
fi

# 创建数据目录
mkdir -p ~/.openclaw/workspace/trading_data

# 检查当前持仓（提醒用户）
echo ""
echo "⚠️  重要提醒:"
echo "请确认币安账户中的期货持仓已处理！"
echo ""
echo "当前现货余额（来自API）:"
echo "  USDT: ~$40.41"
echo "  BTC:  ~$9.15"
echo "  总计: ~$49.56"
echo ""

# 询问确认
read -p "确认期货持仓已平仓，继续启动? (y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "❌ 已取消"
    exit 1
fi

echo ""
echo "🚀 启动交易机器人..."
echo "按 Ctrl+C 停止"
echo ""

# 启动机器人
cd ~/.openclaw/workspace
python3 safe_trading_bot_v2.py

echo ""
echo "✅ 机器人已停止"
