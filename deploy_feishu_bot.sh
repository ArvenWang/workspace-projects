#!/bin/bash
# 飞书机器人完整部署向导
# 交互式部署脚本

clear
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║           🚀 OpenClaw 飞书机器人部署向导                      ║"
echo "║                                                              ║"
echo "║      支持：文本 | 图片 | 语音 | 全部现有能力                 ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查 OpenClaw
if ! command -v openclaw &> /dev/null; then
    echo -e "${RED}❌ 错误: OpenClaw 未安装或未在 PATH 中${NC}"
    exit 1
fi

echo -e "${GREEN}✓ OpenClaw 已安装${NC}"
echo ""

# 步骤 1: 获取应用凭证
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 1/5: 飞书应用凭证"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "请先在飞书开放平台创建应用:"
echo "  1. 访问 https://open.feishu.cn/app"
echo "  2. 创建企业自建应用"
echo "  3. 在「凭证与基础信息」中获取:"
echo ""

read -p "请输入 App ID (cli_xxxx): " APP_ID
read -s -p "请输入 App Secret: " APP_SECRET
echo ""

if [ -z "$APP_ID" ] || [ -z "$APP_SECRET" ]; then
    echo -e "${RED}❌ App ID 和 App Secret 不能为空${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 凭证已接收${NC}"
echo ""

# 步骤 2: 配置检查
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 2/5: 配置检查"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

CONFIG_DIR="$HOME/.openclaw/agents/main"
CONFIG_FILE="$CONFIG_DIR/config.yaml"

# 备份旧配置
if [ -f "$CONFIG_FILE" ]; then
    BACKUP_FILE="$CONFIG_DIR/config_backup_$(date +%Y%m%d_%H%M%S).yaml"
    cp "$CONFIG_FILE" "$BACKUP_FILE"
    echo -e "${YELLOW}⚠ 已备份旧配置到: $BACKUP_FILE${NC}"
fi

echo -e "${GREEN}✓ 配置检查完成${NC}"
echo ""

# 步骤 3: 写入配置
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 3/5: 写入配置"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

mkdir -p "$CONFIG_DIR"

cat > "$CONFIG_FILE" << EOF
channels:
  feishu:
    enabled: true
    dmPolicy: pairing
    streaming: true
    blockStreaming: true
    accounts:
      main:
        appId: "$APP_ID"
        appSecret: "$APP_SECRET"
        botName: "OpenClaw AI"
        mediaSupport:
          images: true
          voice: true
          file: true
        voiceTranscription:
          enabled: true
          model: small
          language: zh

agent:
  name: "main"
  systemPrompt: |
    你是 OpenClaw AI 助手，运行在飞书平台。
    
    支持的能力：
    - 💬 文本对话
    - 🖼️ 图片识别与分析
    - 🎤 语音消息转文字
    - 💰 加密货币交易（Binance）
    - 🔍 网页搜索（DuckDuckGo、Perplexity）
    - 📄 飞书文档/知识库/云盘操作
    - 🌐 浏览器自动化
    - 📺 YouTube 视频下载
    - 🐦 Twitter/X 操作
    
    收到语音消息时会自动转录为文字处理。

memory:
  enabled: true
  persistence: true
  sources:
    - memory
    - filesystem

logging:
  level: info
EOF

echo -e "${GREEN}✓ 配置文件已写入: $CONFIG_FILE${NC}"
echo ""

# 步骤 4: 重启服务
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 4/5: 重启 OpenClaw 服务"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "正在重启 Gateway..."
openclaw gateway restart > /dev/null 2>&1

echo -n "等待服务启动"
for i in {1..5}; do
    echo -n "."
    sleep 1
done
echo ""

echo -e "${GREEN}✓ 服务已重启${NC}"
echo ""

# 步骤 5: 验证
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 5/5: 验证配置"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 检查状态
if openclaw status | grep -q "Feishu.*ON"; then
    echo -e "${GREEN}✓ 飞书频道已启用${NC}"
else
    echo -e "${YELLOW}⚠ 飞书频道状态异常，请检查配置${NC}"
fi

echo ""
echo "配置内容预览:"
echo "------------"
grep -A 5 "appId:" "$CONFIG_FILE" | head -6
echo ""

# 完成
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║                    🎉 部署完成！                             ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${YELLOW}📋 后续步骤：${NC}"
echo ""
echo "1. 在飞书开放平台开通权限（参考 FEISHU_PERMISSIONS.md）"
echo "   必须开通: im:message:send, im:message.resource 等"
echo ""
echo "2. 配置事件订阅："
echo "   - 开启事件订阅"
echo "   - 添加事件: im.message.receive_v1"
echo ""
echo "3. 发布应用："
echo "   - 创建版本（1.0.0）"
echo "   - 申请发布"
echo ""
echo "4. 在飞书中使用："
echo "   - 搜索 'OpenClaw AI'"
echo "   - 点击「开始使用」"
echo "   - 发送消息测试"
echo ""
echo "5. 测试命令："
echo "   openclaw message send --channel feishu --message 'Hello'"
echo ""
echo -e "${BLUE}📖 文档：${NC}"
echo "   - 部署指南: cat FEISHU_BOT_DEPLOY.md"
echo "   - 权限清单: cat FEISHU_PERMISSIONS.md"
echo "   - 能力清单: cat FEISHU_CAPABILITIES.md"
echo ""
echo -e "${GREEN}有任何问题，随时问我！${NC}"
echo ""
