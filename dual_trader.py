#!/usr/bin/env python3
"""
双向持仓模式交易 - 针对 dualSidePosition=True
"""

import time
import json
import base64
import urllib.request
import urllib.error
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import os

# 配置
API_KEY = "Rzb1qhBd3BkIGLCO4rH7pTjPt1KZpq7lbgfIp0np81gOdq6xF9p7oFzqXq0cpLvs"
PRIVATE_KEY_B64 = "MC4CAQAwBQYDK2VwBCIEIISJgEmcDMko/bVi5n3nkDxNHpztDrqB08Ug5gGLDjdF"
DATA_DIR = os.path.expanduser("~/.openclaw/workspace/trading_data")
INITIAL_BALANCE = 50

# 初始化密钥
full_key = base64.b64decode(PRIVATE_KEY_B64)
seed = full_key[16:48]
private_key = Ed25519PrivateKey.from_private_bytes(seed)

def log(msg, level="INFO"):
    ts = time.strftime('%H:%M:%S')
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    with open(f"{DATA_DIR}/DUAL_TRADING.log", "a") as f:
        f.write(line + "\n")

def api_call(endpoint, params, method="GET", max_retries=10):
    """API调用 - 双向持仓模式"""
    for attempt in range(max_retries):
        try:
            # 获取服务器时间
            req = urllib.request.Request("https://api.binance.com/api/v3/time")
            with urllib.request.urlopen(req, timeout=5) as r:
                ts = json.loads(r.read().decode())['serverTime']
            
            params['timestamp'] = ts
            query = '&'.join([f"{k}={v}" for k, v in params.items()])
            sig = base64.b64encode(private_key.sign(query.encode('utf-8'))).decode('utf-8')
            
            if method == "GET":
                url = f"https://fapi.binance.com{endpoint}?{query}&signature={sig}"
                req = urllib.request.Request(url, headers={'X-MBX-APIKEY': API_KEY})
            else:
                url = f"https://fapi.binance.com{endpoint}"
                data = f"{query}&signature={sig}"
                req = urllib.request.Request(url, data=data.encode('utf-8'),
                                             headers={'X-MBX-APIKEY': API_KEY, 
                                                     'Content-Type': 'application/x-www-form-urlencoded'},
                                             method='POST')
            
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            err = json.loads(e.read().decode())
            if err.get('code') == -1022 and attempt < max_retries - 1:
                time.sleep(0.3)
                continue
            return {"error": f"{err.get('code')} - {err.get('msg')}"}
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(0.3)
                continue
            return {"error": str(e)}
    return {"error": "Max retries"}

def get_account():
    return api_call("/fapi/v2/account", {})

def get_price(symbol="BTCUSDT"):
    result = api_call("/fapi/v1/ticker/price", {"symbol": symbol})
    return float(result['price']) if 'price' in result else None

def get_positions():
    """获取双向持仓"""
    result = api_call("/fapi/v2/positionRisk", {})
    positions = {}
    if isinstance(result, list):
        for p in result:
            amt_long = float(p.get('positionAmt', 0))
            amt_short = float(p.get('positionAmt', 0))  # 双向模式下需要检查两个字段
            if amt_long != 0 or amt_short != 0:
                positions[p['symbol']] = p
    return positions

def open_long(symbol, quantity):
    """开多 - 双向模式"""
    log(f"🟢 开多 {symbol} {quantity}")
    return api_call("/fapi/v1/order", {
        "symbol": symbol,
        "side": "BUY",
        "positionSide": "LONG",  # 双向模式必须指定
        "type": "MARKET",
        "quantity": quantity
    }, "POST")

def open_short(symbol, quantity):
    """开空 - 双向模式"""
    log(f"🔴 开空 {symbol} {quantity}")
    return api_call("/fapi/v1/order", {
        "symbol": symbol,
        "side": "SELL",
        "positionSide": "SHORT",  # 双向模式必须指定
        "type": "MARKET",
        "quantity": quantity
    }, "POST")

def close_long(symbol, quantity):
    """平多 - 双向模式"""
    log(f"🔴 平多 {symbol} {quantity}")
    return api_call("/fapi/v1/order", {
        "symbol": symbol,
        "side": "SELL",
        "positionSide": "LONG",  # 平多也是LONG side
        "type": "MARKET",
        "quantity": quantity
    }, "POST")

def close_short(symbol, quantity):
    """平空 - 双向模式"""
    log(f"🔴 平空 {symbol} {quantity}")
    return api_call("/fapi/v1/order", {
        "symbol": symbol,
        "side": "BUY",
        "positionSide": "SHORT",  # 平空也是SHORT side
        "type": "MARKET",
        "quantity": quantity
    }, "POST")

def main():
    log("="*60)
    log("🔥🔥🔥 双向持仓模式交易启动 🔥🔥🔥")
    log("="*60)
    
    # 检查账户
    account = get_account()
    if 'totalWalletBalance' not in account:
        log(f"获取账户失败: {account}", "ERROR")
        return
    
    balance = float(account['totalWalletBalance'])
    log(f"✅ 连接成功! 余额: {balance:.2f} USDT")
    log(f"📊 模式: 双向持仓 (dualSidePosition=True)")
    
    # 获取价格
    price = get_price("BTCUSDT")
    if not price:
        log("无法获取价格", "ERROR")
        return
    
    log(f"📊 BTC价格: ${price:,.2f}")
    
    # 执行第一笔交易
    quantity = 0.001
    log(f"🎯 开多 {quantity} BTC...")
    
    order = open_long("BTCUSDT", quantity)
    
    if 'orderId' in order:
        avg_price = order.get('avgPrice', price)
        log(f"✅✅✅ 首次交易成功!!!")
        log(f"   OrderID: {order['orderId']}")
        log(f"   成交: ${avg_price}")
        log(f"   方向: 做多 BTC {quantity}")
        
        # 记录
        with open(f"{DATA_DIR}/SUCCESS_TRADES.log", "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - 开多 BTC {quantity} @ ${avg_price}\n")
        
        # 10秒后平仓测试
        log("等待10秒后平仓...")
        time.sleep(10)
        
        close = close_long("BTCUSDT", quantity)
        if 'orderId' in close:
            log(f"✅ 平仓成功! 测试完成")
        else:
            log(f"平仓失败: {close.get('error', close)}", "WARN")
    else:
        log(f"❌ 交易失败: {order.get('error', order)}", "ERROR")

if __name__ == "__main__":
    main()
