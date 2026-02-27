#!/bin/bash
# 语音通知脚本

LOG_FILE="$HOME/.openclaw/workspace/trading_data/ACTIVE_TRADING.log"
LAST_CHECK=$(date +%s)

while true; do
    # 检查日志中是否有重要事件
    if [ -f "$LOG_FILE" ]; then
        NEW_EVENTS=$(tail -5 "$LOG_FILE" | grep -E "(开仓成功|止盈|止损|余额)" | tail -1)
        if [ -n "$NEW_EVENTS" ]; then
            # macOS语音播报
            say -v "Ting-Ting" "$NEW_EVENTS" 2>/dev/null || \
            say "$NEW_EVENTS" 2>/dev/null || \
            echo "$NEW_EVENTS"
        fi
    fi
    sleep 30
done
