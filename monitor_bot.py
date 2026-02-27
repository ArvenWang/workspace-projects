#!/usr/bin/env python3
"""
机器人盯盘系统 - 低Token消耗版本
只监控，不决策，触发预警时才通知AI
"""

import requests
import time
import json
import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from datetime import datetime
import os

API_KEY = "Rzb1qhBd3BkIGLCO4rH7pTjPt1KZpq7lbgfIp0np81gOdq6xF9p7oFzqXq0cpLvs"
PRIVATE_KEY_B64 = "MC4CAQAwBQYDK2VwBCIEIISJgEmcDMko/bVi5n3nkDxNHpztDrqB08Ug5gGLDjdF"

full_key = base64.b64decode(PRIVATE_KEY_B64)
seed = full_key[16:48]
private_key = Ed25519PrivateKey.from_private_bytes(seed)

DATA_DIR = "/Users/wangjingwen/.openclaw/workspace/trading_data"

class MonitorBot:
    def __init__(self):
        self.price_history = []
        self.last_alert_time = 0
        self.alert_cooldown = 300  # 5分钟内不重复预警
        
    def log(self, msg, alert=False):
        ts = datetime.now().strftime('%H:%M:%S')
        line = f"[{ts}] {msg}"
        print(line)
        
        # 写入日志
        with open(f"{DATA_DIR}/monitor_bot.log", "a") as f:
            f.write(line + "\n")
        
        # 重要事件写入预警文件（供AI读取）
        if alert:
            with open(f"{DATA_DIR}/alerts.txt", "a") as f:
                f.write(f"{datetime.now().isoformat()} | {msg}\n")
            # 语音播报
            os.system(f'say "{msg}" 2>/dev/null')
    
    def get_server_time(self):
        try:
            r = requests.get("https://api.binance.com/api/v3/time", timeout=5)
            return r.json()['serverTime']
        except:
            return int(time.time() * 1000)
    
    def api_call(self, params, method="GET"):
        for _ in range(3):
            try:
                ts = self.get_server_time()
                params['timestamp'] = ts
                query = '&'.join([f"{k}={v}" for k, v in params.items()])
                sig = base64.b64encode(private_key.sign(query.encode('utf-8'))).decode('utf-8')
                
                headers = {'X-MBX-APIKEY': API_KEY}
                
                if method == "GET":
                    url = f"https://fapi.binance.com/fapi/v2/account?{query}&signature={sig}"
                    r = requests.get(url, headers=headers, timeout=10)
                else:
                    url = "https://fapi.binance.com/fapi/v1/order"
                    data = f"{query}&signature={sig}"
                    headers['Content-Type'] = 'application/x-www-form-urlencoded'
                    r = requests.post(url, data=data, headers=headers, timeout=10)
                
                result = r.json()
                if 'code' in result and result['code'] == -1022:
                    time.sleep(0.5)
                    continue
                return result
            except:
                time.sleep(1)
        return {}
    
    def get_btc_price(self):
        try:
            r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=5)
            return float(r.json()['price'])
        except:
            return None
    
    def check_alerts(self, price, position=None):
        """检查是否需要预警"""
        current_time = time.time()
        
        # 冷却检查
        if current_time - self.last_alert_time < self.alert_cooldown:
            return
        
        alerts = []
        
        # 1. 价格暴涨预警 (>3% in 5min)
        if len(self.price_history) >= 2:
            old_price = self.price_history[-2]
            change = (price - old_price) / old_price * 100
            if abs(change) > 3:
                direction = "暴涨" if change > 0 else "暴跌"
                alerts.append(f"{direction} {change:.2f}%")
        
        # 2. 持仓止盈止损预警
        if position:
            entry = float(position.get('entryPrice', 0))
            if entry > 0:
                pnl_pct = (price - entry) / entry * 100
                if pnl_pct >= 4:
                    alerts.append(f"达到止盈线 +{pnl_pct:.2f}%")
                elif pnl_pct <= -2:
                    alerts.append(f"触发止损线 {pnl_pct:.2f}%")
        
        # 3. 突破关键价位
        key_levels = [65000, 66000, 67000, 68000]
        for level in key_levels:
            if abs(price - level) < 100:
                alerts.append(f"接近关键价位 ${level}")
                break
        
        # 发送预警
        if alerts:
            self.last_alert_time = current_time
            for alert in alerts:
                self.log(f"🚨 ALERT: {alert} (BTC: ${price:,.2f})", alert=True)
    
    def run(self):
        self.log("="*60)
        self.log("🤖 机器人盯盘系统启动")
        self.log("="*60)
        self.log("模式: 监控+预警，AI介入决策")
        self.log("检查间隔: 5分钟")
        self.log("="*60)
        
        cycle = 0
        while True:
            try:
                cycle += 1
                
                # 获取价格
                price = self.get_btc_price()
                if not price:
                    time.sleep(10)
                    continue
                
                self.price_history.append(price)
                if len(self.price_history) > 100:
                    self.price_history = self.price_history[-100:]
                
                # 每5分钟记录一次（不消耗Token）
                if cycle % 5 == 0:
                    self.log(f"📊 BTC: ${price:,.2f}")
                
                # 获取持仓（每小时一次，减少API调用）
                position = None
                if cycle % 12 == 0:  # 每小时
                    account = self.api_call({})
                    if 'positions' in account:
                        for p in account['positions']:
                            if float(p.get('positionAmt', 0)) != 0:
                                position = p
                                entry = float(p['entryPrice'])
                                amt = float(p['positionAmt'])
                                self.log(f"💼 持仓: {amt} BTC @ ${entry:,.2f}")
                                break
                
                # 检查预警（关键！触发时才需要AI介入）
                self.check_alerts(price, position)
                
                # 睡眠1分钟
                time.sleep(60)
                
            except Exception as e:
                self.log(f"❌ 错误: {str(e)[:50]}")
                time.sleep(10)

if __name__ == "__main__":
    bot = MonitorBot()
    bot.run()
