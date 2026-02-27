#!/bin/bash
# 腾讯云技能完整部署脚本

echo "🌩️ 腾讯云技能部署"
echo "=================="
echo ""

# 检查并安装依赖
echo "📦 检查依赖..."

# 检查 TCCLI
if ! command -v tccli &> /dev/null; then
    echo "安装 TCCLI..."
    pip3 install tccli
else
    echo "✓ TCCLI 已安装"
fi

# 检查 paramiko (用于 SSH)
if ! python3 -c "import paramiko" 2>/dev/null; then
    echo "安装 paramiko..."
    pip3 install paramiko
else
    echo "✓ paramiko 已安装"
fi

# 检查 scp (用于文件传输)
if ! python3 -c "import scp" 2>/dev/null; then
    echo "安装 scp..."
    pip3 install scp
else
    echo "✓ scp 已安装"
fi

echo ""
echo "✅ 依赖检查完成"
echo ""
echo "📋 下一步：配置腾讯云凭证"
echo ""
echo "运行以下命令配置："
echo "  ./setup_tencent_cloud.sh"
echo ""
echo "或直接执行："
echo "  python3 tencent_cloud_manager.py --configure --secret-id YOUR_ID --secret-key YOUR_KEY"
