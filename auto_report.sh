#!/bin/bash
# 自动汇报脚本 - 解决准时汇报问题

# 获取当前时间
TIME=$(date '+%H:%M')
DATE=$(date '+%Y-%m-%d')

# 生成汇报内容
REPORT="📊 ${TIME} 定时汇报

$(python3 /Users/wangjingwen/.openclaw/workspace/stats_tracker.py report 2>/dev/null || echo '统计生成中...')

---
⏰ 这是自动发送的定时汇报"

# 使用openclaw发送消息
# 注意：需要正确的channel和target配置
/Users/wangjingwen/.nvm/versions/node/v24.13.1/bin/openclaw message send \
  --channel feishu \
  --message "${REPORT}" \
  2>&1 >> /Users/wangjingwen/.openclaw/workspace/trading_data/report_attempts.log

# 记录尝试
echo "[$(date)] 汇报尝试完成" >> /Users/wangjingwen/.openclaw/workspace/trading_data/report_attempts.log
