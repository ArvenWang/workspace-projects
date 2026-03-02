#!/bin/bash
# 交易机器人启动脚本 - 确保3天持续运行

BOT_DIR="/Users/wangjingwen/.openclaw/workspace"
LOG_FILE="$BOT_DIR/trading_data/bot_launcher.log"
PID_FILE="$BOT_DIR/trading_bot.pid"

echo "$(date): 启动交易机器人" >> $LOG_FILE

cd $BOT_DIR

# 检查是否已在运行
if [ -f $PID_FILE ]; then
    OLD_PID=$(cat $PID_FILE)
    if ps -p $OLD_PID > /dev/null 2>&1; then
        echo "$(date): 机器人已在运行 (PID: $OLD_PID)" >> $LOG_FILE
        exit 0
    fi
fi

# 启动机器人
nohup python3 $BOT_DIR/trading_bot.py > $BOT_DIR/trading_data/bot_output.log 2>&1 &
NEW_PID=$!
echo $NEW_PID > $PID_FILE

echo "$(date): 机器人已启动 (PID: $NEW_PID)" >> $LOG_FILE

# 发送启动通知
echo "🚀 交易机器人已启动 (PID: $NEW_PID)"
echo "日志: $BOT_DIR/trading_data/"
echo "目标: 3天盈利50% (50 USDT → 75 USDT)"
