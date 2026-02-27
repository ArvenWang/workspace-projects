#!/bin/bash
# QA Tester Agent 快速部署脚本

set -e

echo "🧪 QA Tester Agent 部署向导"
echo "=========================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}步骤 1/4: 检查依赖...${NC}"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 未安装${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python3 已安装${NC}"

# 检查 Playwright
if ! python3 -c "import playwright" 2>/dev/null; then
    echo -e "${YELLOW}⚠ Playwright 未安装，正在安装...${NC}"
    pip3 install playwright
    python3 -m playwright install chromium
    echo -e "${GREEN}✓ Playwright 安装完成${NC}"
else
    echo -e "${GREEN}✓ Playwright 已安装${NC}"
fi

# 检查 websockets
if ! python3 -c "import websockets" 2>/dev/null; then
    echo -e "${YELLOW}⚠ websockets 未安装，正在安装...${NC}"
    pip3 install websockets
    echo -e "${GREEN}✓ websockets 安装完成${NC}"
else
    echo -e "${GREEN}✓ websockets 已安装${NC}"
fi

echo ""
echo -e "${YELLOW}步骤 2/4: 创建目录结构...${NC}"

mkdir -p ~/.openclaw/workspace/qa_reports
mkdir -p ~/.openclaw/workspace/agents
mkdir -p ~/.openclaw/workspace/skills/qa-tester

echo -e "${GREEN}✓ 目录结构创建完成${NC}"

echo ""
echo -e "${YELLOW}步骤 3/4: 测试 QA Tester...${NC}"

# 简单测试
python3 ~/.openclaw/workspace/qa_tester.py --mode status 2>/dev/null || echo "跳过状态检查"

echo -e "${GREEN}✓ QA Tester 准备就绪${NC}"

echo ""
echo -e "${YELLOW}步骤 4/4: 启动选项...${NC}"

echo ""
echo "🎉 部署完成！"
echo ""
echo "使用方法:"
echo ""
echo "1️⃣ 快速测试 URL:"
echo "   python3 ~/.openclaw/workspace/qa_tester.py --mode test --url http://localhost:3000"
echo ""
echo "2️⃣ 启动 Webhook 服务器:"
echo "   python3 ~/.openclaw/workspace/qa_tester.py --mode server"
echo ""
echo "3️⃣ 作为 OpenClaw Agent 使用:"
echo "   在 OpenClaw 中选择 'qa-tester' Agent"
echo ""
echo "4️⃣ 从 LangGraph 调用:"
echo "   import requests"
echo "   requests.post('http://localhost:8765/test', json={'url': 'http://localhost:3000'})"
echo ""
echo "📁 相关文件:"
echo "   - 测试脚本: ~/.openclaw/workspace/qa_tester.py"
echo "   - Agent配置: ~/.openclaw/workspace/agents/qa-tester.json"
echo "   - 技能文档: ~/.openclaw/workspace/skills/qa-tester/SKILL.md"
echo "   - 报告目录: ~/.openclaw/workspace/qa_reports/"
echo ""
