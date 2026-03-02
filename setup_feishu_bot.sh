#!/bin/bash
# 飞书机器人快速配置脚本
# 用法: ./setup_feishu_bot.sh <app_id> <app_secret>

set -e

APP_ID=${1:-""}
APP_SECRET=${2:-""}

if [ -z "$APP_ID" ] || [ -z "$APP_SECRET" ]; then
    echo "❌ 用法: ./setup_feishu_bot.sh <app_id> <app_secret>"
    echo "   示例: ./setup_feishu_bot.sh cli_a910189bf3e1dbce xxxxxxxxxxxxxxxxxxxxxxxx"
    exit 1
fi

echo "🚀 开始配置飞书机器人..."
echo "   App ID: $APP_ID"
echo ""

# 检查 OpenClaw 是否安装
if ! command -v openclaw &> /dev/null; then
    echo "❌ OpenClaw 未安装或未在 PATH 中"
    exit 1
fi

# 获取配置路径
CONFIG_DIR="$HOME/.openclaw/agents/main"
CONFIG_FILE="$CONFIG_DIR/config.yaml"

# 创建配置目录（如果不存在）
mkdir -p "$CONFIG_DIR"

echo "📝 写入配置文件..."

# 创建配置文件
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
        # 多媒体支持
        mediaSupport:
          images: true
          voice: true
          file: true
        # 语音转文字
        voiceTranscription:
          enabled: true
          model: small
          language: zh

# Agent 配置
agent:
  name: "main"
  systemPrompt: |
    你是 OpenClaw AI 助手，运行在飞书平台。
    
    能力包括：
    - 文本对话
    - 图片识别与分析
    - 语音消息转文字
    - 加密货币交易（Binance）
    - 网页搜索（DuckDuckGo、Perplexity）
    - 飞书文档/知识库/云盘操作
    - 浏览器自动化
    - YouTube 视频下载
    - Twitter/X 操作
    
    收到语音消息时会自动转录为文字处理。
    可以用图片进行视觉分析。
    
# 工具配置
tools:
  # 允许的工具列表
  allow:
    - "*"
  
  # 插件工具
  plugins:
    - feishu_doc
    - feishu_wiki
    - feishu_drive

# 内存配置
memory:
  enabled: true
  persistence: true
  sources:
    - memory
    - filesystem

# 日志配置
logging:
  level: info
  file: "$HOME/.openclaw/logs/openclaw.log"
EOF

echo "✅ 配置文件已创建: $CONFIG_FILE"

# 重启 Gateway
echo "🔄 重启 OpenClaw Gateway..."
openclaw gateway restart

echo ""
echo "⏳ 等待服务启动..."
sleep 3

# 验证配置
echo "🔍 验证配置..."
openclaw status

echo ""
echo "============================================"
echo "🎉 飞书机器人配置完成！"
echo "============================================"
echo ""
echo "📋 后续步骤："
echo "   1. 确保飞书应用已发布"
echo "   2. 在飞书搜索 'OpenClaw AI' 开始使用"
echo "   3. 测试发送消息给机器人"
echo ""
echo "🧪 测试命令："
echo "   openclaw message send --channel feishu --message 'Hello'"
echo ""
echo "📖 查看完整文档："
echo "   cat ~/.openclaw/workspace/FEISHU_BOT_DEPLOY.md"
echo ""
