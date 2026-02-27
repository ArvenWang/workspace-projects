#!/bin/bash
# 腾讯云 CLI 工具安装脚本

echo "🌩️ 腾讯云 CLI (TCCLI) 安装向导"
echo "================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 需要 Python3 环境"
    exit 1
fi

echo "📦 安装 TCCLI..."
pip3 install tccli

echo ""
echo "✅ TCCLI 安装完成"
echo ""
echo "🔧 下一步：配置凭证"
echo ""
echo "请提供以下信息："
echo "  1. SecretId (从腾讯云控制台 → 访问管理 → API密钥管理获取)"
echo "  2. SecretKey"
echo "  3. 默认地域 (如 ap-beijing, ap-shanghai, ap-guangzhou)"
echo ""
echo "配置命令："
echo "  tccli configure"
echo ""
