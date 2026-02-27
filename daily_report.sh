#!/bin/bash
# 每晚22:00交易汇报脚本

BOT_DIR="/Users/wangjingwen/.openclaw/workspace"
REPORT_FILE="$BOT_DIR/trading_data/pnl_summary.json"
LOG_FILE="$BOT_DIR/trading_data/daily_report.log"

echo "$(date): 生成每日报告" >> $LOG_FILE

# 读取最新数据
if [ -f $REPORT_FILE ]; then
    echo "$(date): 交易数据:" >> $LOG_FILE
    tail -20 $REPORT_FILE >> $LOG_FILE
fi

# 检查机器人状态
if [ -f $BOT_DIR/trading_bot.pid ]; then
    PID=$(cat $BOT_DIR/trading_bot.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "$(date): 机器人运行正常 (PID: $PID)" >> $LOG_FILE
    else
        echo "$(date): 机器人已停止，重新启动..." >> $LOG_FILE
        $BOT_DIR/start_trading_bot.sh
    fi
fi

# 发送报告 (这里可以集成飞书/邮件通知)
echo "📊 每日交易报告已生成"
