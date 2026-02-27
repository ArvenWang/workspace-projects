#!/bin/bash
# 腾讯云资源管理 - 快速配置脚本

clear
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║           🌩️ 腾讯云资源管理配置向导                           ║"
echo "║                                                              ║"
echo "║      支持：CVM | 轻量服务器 | COS | 域名 | CDN               ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${YELLOW}步骤 1/5: 安装 TCCLI...${NC}"

# 检查 TCCLI
if ! command -v tccli &> /dev/null; then
    echo -e "${YELLOW}⚠ TCCLI 未安装，正在安装...${NC}"
    pip3 install tccli
    echo -e "${GREEN}✓ TCCLI 安装完成${NC}"
else
    echo -e "${GREEN}✓ TCCLI 已安装${NC}"
fi

echo ""
echo -e "${YELLOW}步骤 2/5: 获取腾讯云凭证...${NC}"
echo ""
echo "请前往腾讯云控制台获取 API 密钥："
echo "  1. 访问 https://console.cloud.tencent.com/cam/capi"
echo "  2. 点击「新建密钥」"
echo "  3. 复制 SecretId 和 SecretKey"
echo ""

read -p "请输入 SecretId (AKID...): " SECRET_ID
read -s -p "请输入 SecretKey: " SECRET_KEY
echo ""

if [ -z "$SECRET_ID" ] || [ -z "$SECRET_KEY" ]; then
    echo -e "${RED}❌ SecretId 和 SecretKey 不能为空${NC}"
    exit 1
fi

echo ""
echo "请选择默认地域："
echo "  1) 北京 (ap-beijing)"
echo "  2) 上海 (ap-shanghai)"
echo "  3) 广州 (ap-guangzhou)"
echo "  4) 香港 (ap-hongkong)"
echo "  5) 新加坡 (ap-singapore)"
read -p "请选择 [1-5]: " REGION_CHOICE

case $REGION_CHOICE in
    1) REGION="ap-beijing" ;;
    2) REGION="ap-shanghai" ;;
    3) REGION="ap-guangzhou" ;;
    4) REGION="ap-hongkong" ;;
    5) REGION="ap-singapore" ;;
    *) REGION="ap-beijing" ;;
esac

echo ""
echo -e "${YELLOW}步骤 3/5: 配置 TCCLI...${NC}"

tccli configure set secretId "$SECRET_ID"
tccli configure set secretKey "$SECRET_KEY"
tccli configure set region "$REGION"
tccli configure set output json

echo -e "${GREEN}✓ TCCLI 配置完成${NC}"

echo ""
echo -e "${YELLOW}步骤 4/5: 保存配置到 OpenClaw...${NC}"

python3 ~/.openclaw/workspace/tencent_cloud_manager.py \
  --configure \
  --secret-id "$SECRET_ID" \
  --secret-key "$SECRET_KEY" \
  --region "$REGION"

echo -e "${GREEN}✓ OpenClaw 配置已保存${NC}"

echo ""
echo -e "${YELLOW}步骤 5/5: 验证配置...${NC}"

# 尝试获取实例列表
RESULT=$(tccli cvm DescribeInstances --limit 1 2>&1)

if echo "$RESULT" | grep -q "InstanceSet"; then
    echo -e "${GREEN}✅ 配置验证成功！${NC}"
    echo ""
    echo "📊 你的腾讯云资源："
    
    # 获取 CVM 数量
    CVM_COUNT=$(tccli cvm DescribeInstances --limit 100 2>/dev/null | grep -o '"InstanceSet"' | wc -l)
    if [ "$CVM_COUNT" -gt 0 ]; then
        echo "  - CVM 云服务器: $CVM_COUNT 台"
    fi
    
    # 获取轻量服务器数量
    LH_COUNT=$(tccli lighthouse DescribeInstances --limit 100 2>/dev/null | grep -o '"InstanceSet"' | wc -l)
    if [ "$LH_COUNT" -gt 0 ]; then
        echo "  - 轻量应用服务器: $LH_COUNT 台"
    fi
    
    # 获取 COS 存储桶数量
    BUCKET_COUNT=$(tccli cos ListBuckets 2>/dev/null | grep -o '"Name"' | wc -l)
    if [ "$BUCKET_COUNT" -gt 0 ]; then
        echo "  - COS 存储桶: $BUCKET_COUNT 个"
    fi
    
else
    echo -e "${RED}❌ 配置验证失败${NC}"
    echo "错误信息: $RESULT"
    echo ""
    echo "请检查："
    echo "  1. SecretId 和 SecretKey 是否正确"
    echo "  2. API 密钥是否有 CVM 访问权限"
    echo "  3. 网络连接是否正常"
    exit 1
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║                    🎉 配置完成！                             ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${YELLOW}📋 使用示例：${NC}"
echo ""
echo "1️⃣ 列出所有云服务器："
echo "   python3 -c \"from tencent_cloud_manager import TencentCloudManager; "
echo "   m = TencentCloudManager(); print(m.cvm_list_instances())\""
echo ""
echo "2️⃣ 使用 TCCLI："
echo "   tccli cvm DescribeInstances"
echo "   tccli lighthouse DescribeInstances"
echo "   tccli cos ListBuckets"
echo ""
echo "3️⃣ 在 OpenClaw 中使用："
echo "   直接询问：\"列出我的腾讯云服务器\""
echo ""
echo -e "${BLUE}📖 文档：${NC}"
echo "   cat ~/.openclaw/workspace/skills/tencent-cloud/SKILL.md"
echo ""
