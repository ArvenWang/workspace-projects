#!/usr/bin/env python3
"""
统计追踪系统 - 记录新模式下的各项指标
"""

import json
import os
from datetime import datetime

DATA_DIR = "/Users/wangjingwen/.openclaw/workspace/trading_data"
STATS_FILE = f"{DATA_DIR}/daily_stats.json"

def init_stats():
    """初始化今日统计"""
    today = datetime.now().strftime('%Y-%m-%d')
    stats = {
        "date": today,
        "start_time": datetime.now().isoformat(),
        "ai_interventions": 0,  # AI介入次数
        "trades_executed": 0,   # 交易执行次数
        "token_consumed": 0,    # Token消耗量
        "start_balance": 0,     # 起始余额
        "current_balance": 0,   # 当前余额
        "alerts_triggered": 0,  # 预警触发次数
        "notes": []
    }
    save_stats(stats)
    return stats

def load_stats():
    """加载统计"""
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'r') as f:
            return json.load(f)
    return init_stats()

def save_stats(stats):
    """保存统计"""
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)

def record_ai_intervention(reason):
    """记录AI介入"""
    stats = load_stats()
    stats["ai_interventions"] += 1
    stats["token_consumed"] += 500  # 估算每次介入消耗500 tokens
    stats["notes"].append(f"{datetime.now().strftime('%H:%M')} - AI介入: {reason}")
    save_stats(stats)

def record_trade(action, symbol, quantity, price):
    """记录交易"""
    stats = load_stats()
    stats["trades_executed"] += 1
    stats["token_consumed"] += 800  # 交易决策+执行约800 tokens
    stats["notes"].append(f"{datetime.now().strftime('%H:%M')} - 交易: {action} {symbol} {quantity} @ ${price}")
    save_stats(stats)

def record_alert():
    """记录预警（机器人自动，不增加token）"""
    stats = load_stats()
    stats["alerts_triggered"] += 1
    save_stats(stats)

def update_balance(balance):
    """更新余额"""
    stats = load_stats()
    if stats["start_balance"] == 0:
        stats["start_balance"] = balance
    stats["current_balance"] = balance
    save_stats(stats)

def get_report():
    """生成报告"""
    stats = load_stats()
    
    pnl = stats["current_balance"] - stats["start_balance"]
    pnl_pct = (pnl / stats["start_balance"] * 100) if stats["start_balance"] > 0 else 0
    
    report = f"""
📊 新模式运行报告 ({stats['date']})
========================================
⏰ 统计时段: {stats['start_time'][:19]} ~ {datetime.now().strftime('%H:%M:%S')}

🔢 关键指标:
  • AI介入次数: {stats['ai_interventions']} 次
  • 交易执行: {stats['trades_executed']} 次
  • 预警触发: {stats['alerts_triggered']} 次
  
💰 收益情况:
  • 起始余额: ${stats['start_balance']:.2f} USDT
  • 当前余额: ${stats['current_balance']:.2f} USDT
  • 盈亏: {pnl:+.2f} USDT ({pnl_pct:+.2f}%)
  
🔥 Token消耗:
  • 总计: {stats['token_consumed']} tokens
  • 对比旧模式: 节省 {(50000 - stats['token_consumed']) / 50000 * 100:.1f}%
  
📝 详细记录:
"""
    for note in stats["notes"][-10:]:  # 最近10条
        report += f"    {note}\n"
    
    report += "========================================"
    return report

if __name__ == "__main__":
    # 初始化或显示报告
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "report":
        print(get_report())
    else:
        init_stats()
        print("✅ 统计追踪已初始化")
