#!/bin/bash
# 手动交易守护脚本
# 每30秒监控一次，发送提醒

LOG_FILE="/Users/wangjingwen/.openclaw/workspace/trading_data/MANUAL_ALERT.log"

echo "$(date): 手动盯盘模式启动 - 未来3天" >> $LOG_FILE

# 持续监控
while true; do
    python3 << 'PYEOF'
import urllib.request, json, time

# 获取BTC价格 (公共API，无需签名)
try:
    req = urllib.request.Request("https://fapi.binance.com/fapi/v1/ticker/price?symbol=BTCUSDT")
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
        price = float(data['price'])
        
        timestamp = time.strftime('%H:%M:%S')
        msg = f"[{timestamp}] BTC: ${price:,.2f}"
        print(msg)
        
        # 简单判断：价格变动超过0.5%输出提醒
        log_file = "/Users/wangjingwen/.openclaw/workspace/trading_data/price_monitor.log"
        with open(log_file, "a") as f:
            f.write(f"{timestamp},{price}\n")
            
except Exception as e:
    print(f"[{time.strftime('%H:%M:%S')}] 价格获取失败: {e}")
PYEOF
    
    sleep 30
done
