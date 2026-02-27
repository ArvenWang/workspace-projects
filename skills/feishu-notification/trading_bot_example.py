#!/usr/bin/env python3
"""
交易机器人飞书通知集成示例
演示如何在交易机器人中使用飞书主动推送
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_notify import notify

# ============ 配置 ============
# 你的飞书用户OpenID（可以从飞书管理后台获取）
MY_FEISHU_ID = "user:ou_d62bc39aafec8dcee9e68c31331e9965"

# 交易群组ID（如果有）
TRADING_GROUP_ID = "chat:oc_xxxxxxxxxxxxxxxx"  # 替换为你的群组ID
# =============================

def send_trade_notification(symbol: str, action: str, price: float, quantity: float, pnl: float = None):
    """发送交易执行通知"""
    pnl_text = f"\n💰 盈亏: {pnl:+.2f} USDT" if pnl else ""
    
    message = f"""🚀 **交易执行通知**

📊 币种: {symbol}
🎯 操作: {action}
💵 价格: {price:,.2f} USDT
📈 数量: {quantity}{pnl_text}

⏰ 时间: {get_current_time()}
"""
    notify(message, target=MY_FEISHU_ID, use_card=True)

def send_price_alert(symbol: str, current_price: float, target_price: float, alert_type: str):
    """发送价格预警"""
    emoji = "🚨" if alert_type == "breakout" else "⚠️"
    direction = "突破" if alert_type == "breakout" else "跌破"
    
    message = f"""{emoji} **价格预警**

📊 {symbol} {direction}目标价位！

• 当前价格: {current_price:,.2f} USDT
• 目标价格: {target_price:,.2f} USDT
• 触发时间: {get_current_time()}

建议关注后续走势。
"""
    notify(message, target=MY_FEISHU_ID, use_card=True)

def send_daily_report(trades: list, total_pnl: float, win_rate: float):
    """发送每日交易报告"""
    trade_count = len(trades)
    
    # 构建交易表格
    trade_rows = []
    for trade in trades[:5]:  # 只显示最近5笔
        status = "✅" if trade.get('pnl', 0) > 0 else "❌"
        trade_rows.append(f"| {trade['symbol']} | {trade['action']} | {trade['pnl']:+.2f} | {status} |")
    
    trade_table = "\n".join(trade_rows) if trade_rows else "| 无交易 | - | - | - |"
    
    message = f"""📊 **每日交易报告**

📅 日期: {get_current_date()}
📈 总交易: {trade_count} 笔
💰 总盈亏: {total_pnl:+.2f} USDT
🎯 胜率: {win_rate:.1f}%

**最近交易:**
| 币种 | 操作 | 盈亏 | 结果 |
|------|------|------|------|
{trade_table}

{'🎉 今日盈利！' if total_pnl > 0 else '😔 今日亏损，明天继续！'}
"""
    notify(message, target=MY_FEISHU_ID, use_card=True)

def send_system_alert(alert_type: str, message: str, severity: str = "warning"):
    """发送系统告警"""
    emoji_map = {
        "critical": "🔴",
        "warning": "🟡", 
        "info": "🔵"
    }
    emoji = emoji_map.get(severity, "⚠️")
    
    content = f"""{emoji} **系统告警**

**类型:** {alert_type}
**级别:** {severity.upper()}
**时间:** {get_current_time()}

{message}

请及时处理。
"""
    notify(content, target=MY_FEISHU_ID, use_card=True)

# ============ 工具函数 ============

def get_current_time():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_current_date():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")

# ============ 使用示例 ============

if __name__ == "__main__":
    print("飞书通知测试示例")
    print("=" * 40)
    
    # 示例1: 交易通知
    print("\n1. 发送交易通知...")
    send_trade_notification(
        symbol="BTC/USDT",
        action="买入",
        price=50234.50,
        quantity=0.1,
        pnl=0
    )
    
    # 示例2: 价格预警
    print("\n2. 发送价格预警...")
    send_price_alert(
        symbol="ETH/USDT",
        current_price=3024.80,
        target_price=3000.00,
        alert_type="breakout"
    )
    
    # 示例3: 每日报告
    print("\n3. 发送每日报告...")
    sample_trades = [
        {"symbol": "BTC/USDT", "action": "买入", "pnl": 125.5},
        {"symbol": "ETH/USDT", "action": "卖出", "pnl": -23.2},
        {"symbol": "SOL/USDT", "action": "买入", "pnl": 45.8},
    ]
    send_daily_report(
        trades=sample_trades,
        total_pnl=148.1,
        win_rate=66.7
    )
    
    # 示例4: 系统告警
    print("\n4. 发送系统告警...")
    send_system_alert(
        alert_type="API连接异常",
        message="Binance API 连接超时，已自动重试3次",
        severity="warning"
    )
    
    print("\n✅ 所有示例消息已发送！")
    print("\n提示: 在你的交易机器人中导入此模块:")
    print("  from feishu_notify import notify")
    print("  notify('消息内容', target='user:your_id')")
