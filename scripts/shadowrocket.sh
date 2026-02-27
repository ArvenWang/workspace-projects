#!/bin/bash
# Shadowrocket 自动启动脚本
# 使用方法: ./scripts/shadowrocket.sh

set -e

echo "🔥 启动 Shadowrocket..."

# 检查是否已在运行
if pgrep -x "Shadowrocket" > /dev/null; then
    echo "✅ Shadowrocket 已在运行"
else
    # 启动应用
    open -a Shadowrocket
    echo "⏳ 等待启动..."
    sleep 5
    
    # 验证启动
    if ! pgrep -x "Shadowrocket" > /dev/null; then
        echo "❌ 启动失败"
        exit 1
    fi
    echo "✅ Shadowrocket 已启动"
fi

# 启用系统代理
echo "🔧 配置系统代理..."
networksetup -setwebproxy "Shadowrocket" 127.0.0.1 1082 2>/dev/null || true
networksetup -setwebproxystate "Shadowrocket" on 2>/dev/null || true

# 配置 Git 代理
echo "🔧 配置 Git 代理..."
git config --global http.proxy http://127.0.0.1:1082
git config --global https.proxy http://127.0.0.1:1082

# 测试连接
echo "🧪 测试连接..."
sleep 2

if curl -sI --proxy http://127.0.0.1:1082 https://github.com > /dev/null 2>&1; then
    echo "✅ 网络连接正常"
    echo "🎉 Shadowrocket 启动完成！"
    exit 0
else
    echo "⚠️ 连接测试失败，可能需要手动检查"
    exit 1
fi
