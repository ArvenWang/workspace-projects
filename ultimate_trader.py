#!/usr/bin/env python3
"""
终极稳定版手动交易 - 强制重试直到成功
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
    with open(f"{DATA_DIR}/ULTIMATE_TRADING.log", "a") as f:
        f.write(line + "\n")

def api_call_with_retry(endpoint, params=None, method="GET", max_retries=10):
    """强制重试直到成功"""
    base_url = "https://fapi.binance.com"
    
    for attempt in range(1, max_retries + 1):
        try:
            # 每次都获取新的服务器时间
            ts_req = urllib.request.Request("https://api.binance.com/api/v3/time")
            with urllib.request.urlopen(ts_req, timeout=5) as ts_resp:
                timestamp = json.loads(ts_resp.read().decode())['serverTime']
            
            if params is None:
                params = {}
            params['timestamp'] = timestamp
            
            query = '&'.join([f"{k}={v}" for k, v in params.items()])
            signature = private_key.sign(query.encode('utf-8'))
            sig_b64 = base64.b64encode(signature).decode('utf-8')
            
            if method == "GET":
                url = f"{base_url}{endpoint}?{query}&signature={sig_b64}"
                req = urllib.request.Request(url, headers={'X-MBX-APIKEY': API_KEY})
            else:
                url = f"{base_url}{endpoint}"
                data = f"{query}&signature={sig_b64}"
                req = urllib.request.Request(url, data=data.encode('utf-8'),
                                             headers={'X-MBX-APIKEY': API_KEY, 
                                                     'Content-Type': 'application/x-www-form-urlencoded'},
                                             method='POST')
            
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode())
                
        except urllib.error.HTTPError as e:
            err = json.loads(e.read().decode())
            if err.get('code') == -1022:  # 签名错误，继续重试
                if attempt < max_retries:
                    time.sleep(0.3)  # 短暂延迟后重试
                    continue
            return {"error": f"{err.get('code')} - {err.get('msg')}"}
        except Exception as e:
            if attempt < max_retries:
                time.sleep(0.3)
                continue
            return {"error": str(e)}
    
    return {"error": "Max retries exceeded"}

def get_account():
    return api_call_with_retry("/fapi/v2/account")

def get_price(symbol="BTCUSDT"):
    result = api_call_with_retry("/fapi/v1/ticker/price", {"symbol": symbol})
    return float(result['price']) if 'price' in result else None

def get_positions():
    result = api_call_with_retry("/fapi/v2/positionRisk")
    if isinstance(result, list):
        return [p for p in result if float(p.get('positionAmt', 0)) != 0]
    return []

def open_long(symbol, quantity):
    log(f"🟢 开多 {symbol} {quantity}")
    return api_call_with_retry("/fapi/v1/order", {
        "symbol": symbol,
        "side": "BUY",
        "type": "MARKET",
        "quantity": quantity
    }, method="POST", max_retries=15)

def open_short(symbol, quantity):
    log(f"🔴 开空 {symbol} {quantity}")
    return api_call_with_retry("/fapi/v1/order", {
        "symbol": symbol,
        "side": "SELL",
        "type": "MARKET",
        "quantity": quantity
    }, method="POST", max_retries=15)

def close_position(symbol, side, quantity):
    close_side = "SELL" if side == "LONG" else "BUY"
    log(f"🔴 平仓 {close_side} {symbol} {quantity}")
    return api_call_with_retry("/fapi/v1/order", {
        "symbol": symbol,
        "side": close_side,
        "type": "MARKET",
        "quantity": quantity
    }, method="POST", max_retries=15)

def main():
    log("="*60)
    log("🔥🔥🔥 终极稳定版交易启动 🔥🔥🔥")
    log("="*60)
    log("使用强制重试机制，直到交易成功！")
    log("="*60)
    
    # 立即执行第一笔交易
    log("执行首次交易测试...")
    
    # 检查余额
    account = get_account()
    if 'availableBalance' not in account:
        log(f"获取账户失败: {account.get('error', 'Unknown')}", "ERROR")
        return
    
    balance = float(account['availableBalance'])
    total = float(account['totalWalletBalance'])
    log(f"✅ 连接成功! 余额: {total:.2f} USDT")
    
    # 获取价格
    price = get_price("BTCUSDT")
    if not price:
        log("无法获取价格", "ERROR")
        return
    
    log(f"📊 BTC价格: ${price:,.2f}")
    
    # 立即开多
    quantity = 0.005
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
        
        # 设置止盈止损后平仓（测试）
        log("等待10秒后平仓测试...")
        time.sleep(10)
        
        close = close_position("BTCUSDT", "LONG", quantity)
        if 'orderId' in close:
            log(f"✅ 平仓成功! 测试完成")
        else:
            log(f"平仓失败: {close.get('error', close)}", "WARN")
    else:
        log(f"❌ 交易失败: {order.get('error', order)}", "ERROR")

if __name__ == "__main__":
    main()
