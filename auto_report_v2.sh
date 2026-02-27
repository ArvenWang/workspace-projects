#!/bin/bash
# 自动汇报脚本 v2 - 使用正确的target

TARGET="ou_d62bc39aafec8dcee8dcee9e68c31331e9965"
TIME=$(date '+%H:%M')
DATE=$(date '+%Y-%m-%d')

# 生成汇报内容
REPORT="📊 ${TIME} 自动汇报

$(python3 /Users/wangjingwen/.openclaw/workspace/stats_tracker.py report 2>/dev/null || echo '统计生成中...')

---
🤖 这是定时自动发送的汇报"

# 发送消息
/Users/wangjingwen/.nvm/versions/node/v24.13.1/bin/openclaw message send \
  --channel feishu \
  --target "${TARGET}" \
  --message "${REPORT}" \
  2>&1 | tee -a /Users/wangjingwen/.openclaw/workspace/trading_data/report_attempts.log

echo "[$(date)] 汇报尝试完成" >> /Users/wangjingwen/.openclaw/workspace/trading_data/report_attempts.log
