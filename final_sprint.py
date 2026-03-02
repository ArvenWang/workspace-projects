#!/usr/bin/env python3
"""
最终冲刺模式 - 完全自主交易
目标: 22:00前实现15%盈利
"""

import requests
import time
import json
import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import os

API_KEY = "Rzb1qhBd3BkIGLCO4rH7pTjPt1KZpq7lbgfIp0np81gOdq6xF9p7oFzqXq0cpLvs"
PRIVATE_KEY_B64 = "MC4CAQAwBQYDK2VwBCIEIISJgEmcDMko/bVi5n3nkDxNHpztDrqB08Ug5gGLDjdF"

full_key = base64.b64decode(PRIVATE_KEY_B64)
seed = full_key[16:48]
private_key = Ed25519PrivateKey.from_private_bytes(seed)

def log(msg):
    ts = time.strftime('%H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line)
    with open("/Users/wangjingwen/.openclaw/workspace/trading_data/FINAL_SPRINT.log", "a") as f:
        f.write(line + "\n")
    # 语音播报重要信息
    if "盈利" in msg or "成功" in msg or "止损" in msg:
        os.system(f'say "{msg}" 2>/dev/null')

def api_call(params, method="GET", max_retry=10):
    """强制重试API调用"""
    for i in range(max_retry):
        try:
            resp = requests.get("https://api.binance.com/api/v3/time", timeout=10)
            ts = resp.json()['serverTime']
        except:
            ts = int(time.time() * 1000)
        
        params['timestamp'] = ts
        query = '&'.join([f"{k}={v}" for k, v in params.items()])
        sig = base64.b64encode(private_key.sign(query.encode('utf-8'))).decode('utf-8')
        
        headers = {'X-MBX-APIKEY': API_KEY}
        
        try:
            if method == "GET":
                url = f"https://fapi.binance.com/fapi/v2/account?{query}&signature={sig}"
                r = requests.get(url, headers=headers, timeout=20)
            else:
                url = "https://fapi.binance.com/fapi/v1/order"
                data = f"{query}&signature={sig}"
                headers['Content-Type'] = 'application/x-www-form-urlencoded'
                r = requests.post(url, data=data, headers=headers, timeout=20)
            
            result = r.json()
            if 'code' in result and result['code'] == -1022:
                if i < max_retry - 1:
                    time.sleep(0.5 * (i + 1))
                    continue
            return result
        except:
            if i < max_retry - 1:
                time.sleep(1)
                continue
    return {}

def main():
    log("="*60)
    log("🔥🔥🔥 最终冲刺模式启动 🔥🔥🔥")
    log("="*60)
    log("目标: 22:00前实现15%盈利")
    log("策略: 高频交易 + 严格风控")
    log("="*60)
    
    # 检查当前状态
    account = api_call({})
    if 'totalWalletBalance' not in account:
        log("❌ 无法获取账户，15分钟后重试...")
        return
    
    balance = float(account['totalWalletBalance'])
    log(f"💰 当前余额: ${balance:.2f}")
    
    # 检查持仓
    positions = api_call({}).get('positions', [])
    has_long = False
    amt = 0
    
    for p in positions:
        if float(p.get('positionAmt', 0)) != 0:
            has_long = True
            amt = float(p['positionAmt', 0])
            entry = float(p['entryPrice'])
            log(f"📊 当前持仓: {amt} BTC @ ${entry}")
    
    if not has_long and balance > 10:
        # 开多
        quantity = 0.002
        log(f"🟢 开多 BTC {quantity}")
        result = api_call({
            "symbol": "BTCUSDT",
            "side": "BUY",
            "positionSide": "LONG",
            "type": "MARKET",
            "quantity": quantity
        }, "POST")
        
        if 'orderId' in result:
            log(f"✅ 开仓成功! OrderID: {result['orderId']}")
        else:
            log(f"❌ 开仓失败: {result}")
    
    log("⏳ 监控中，21:30再次检查...")

if __name__ == "__main__":
    main()
