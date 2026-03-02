
========================================
🚀 交易机器人启动确认
========================================

启动时间: 2026-02-23 11:20:04
运行时长: 3天 (至 2026-02-26 23:59)

📊 交易参数:
- 初始资金: 50 USDT
- 目标盈利: 50% (75 USDT)
- 杠杆: 5x
- 监控间隔: 30秒
- 交易对: BTCUSDT

⚙️ 策略配置:
- 趋势跟踪 + 突破交易
- 止盈: 5%
- 止损: 2%
- 日最大亏损: 15 USDT
- 单笔仓位: 10-20%资金

📁 文件位置:
- 主程序: ~/.openclaw/workspace/trading_bot.py
- 交易日志: ~/.openclaw/workspace/trading_data/trades_YYYYMMDD.log
- 价格数据: ~/.openclaw/workspace/trading_data/prices_BTCUSDT.csv
- 盈亏统计: ~/.openclaw/workspace/trading_data/pnl_summary.json

⏰ 自动任务:
- 每2小时简报 (写入日志)
- 每晚22:00详细报告
- 每30分钟健康检查

🔧 管理命令:
- 查看状态: ps -p $(cat ~/.openclaw/workspace/trading_bot.pid)
- 查看日志: tail -f ~/.openclaw/workspace/trading_data/bot_output.log
- 停止机器人: kill $(cat ~/.openclaw/workspace/trading_bot.pid)
- 重启机器人: ~/.openclaw/workspace/start_trading_bot.sh

进程PID: 77754

========================================

