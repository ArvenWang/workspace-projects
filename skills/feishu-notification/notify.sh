#!/bin/bash
# 飞书消息发送快捷脚本
# Usage: ./notify.sh "消息内容"
# Usage: ./notify.sh -c "## 标题\n内容"  # 卡片格式

# 默认接收者（修改为你的飞书ID）
DEFAULT_TARGET="user:ou_d62bc39aafec8dcee9e68c31331e9965"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 解析参数
USE_CARD=false
MESSAGE=""
TARGET="$DEFAULT_TARGET"

while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--card)
            USE_CARD=true
            shift
            ;;
        -t|--target)
            TARGET="$2"
            shift 2
            ;;
        -h|--help)
            echo "用法: $0 [选项] <消息内容>"
            echo ""
            echo "选项:"
            echo "  -c, --card       使用卡片格式发送"
            echo "  -t, --target     指定接收者 (默认: $DEFAULT_TARGET)"
            echo "  -h, --help       显示帮助"
            echo ""
            echo "示例:"
            echo "  $0 'Hello World'"
            echo "  $0 -c '## 标题\n内容'"
            echo "  $0 -t 'chat:group_id' '群组消息'"
            exit 0
            ;;
        *)
            MESSAGE="$1"
            shift
            ;;
    esac
done

if [ -z "$MESSAGE" ]; then
    echo -e "${RED}错误: 请提供消息内容${NC}"
    echo "用法: $0 '消息内容'"
    exit 1
fi

# 构建命令
if [ "$USE_CARD" = true ]; then
    RENDER_MODE="--renderMode card"
else
    RENDER_MODE=""
fi

# 发送消息
echo "正在发送消息到 $TARGET..."

openclaw message send \
    --channel feishu \
    --target "$TARGET" \
    --message "$MESSAGE" \
    $RENDER_MODE

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 消息发送成功${NC}"
else
    echo -e "${RED}❌ 消息发送失败${NC}"
    exit 1
fi
