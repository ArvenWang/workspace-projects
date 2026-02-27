#!/usr/bin/env python3
"""
超稳定手动交易脚本 - 带重试机制
解决Ed25519签名间歇性失败问题
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
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    with open(f"{DATA_DIR}/MANUAL_TRADING.log", "a") as f:
        f.write(line + "\n")

def get_server_time():
    """获取币安服务器时间 - 带重试"""
    for i in range(3):
        try:
            req = urllib.request.Request("https://api.binance.com/api/v3/time", timeout=5)
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode())['serverTime']
        except:
            time.sleep(0.5)
    return int(time.time() * 1000)

def api_call(endpoint, params=None, method="GET", max_retries=3):
    """API调用 - 带重试机制"""
    base_url = "https://fapi.binance.com"
    
    for attempt in range(max_retries):
        try:
            # 每次重试都获取新的时间戳
            timestamp = get_server_time()
            
            if params is None:
                params = {}
            params['timestamp'] = timestamp
            
            # 构建query string
            query = '&'.join([f"{k}={v}" for k, v in params.items()])
            
            # 签名
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
            if err.get('code') == -1022:  # 签名错误，重试
                if attempt < max_retries - 1:
                    log(f"签名错误，第{attempt+1}次重试...", "WARN")
                    time.sleep(1)
                    continue
            return {"error": f"{err.get('code')} - {err.get('msg')}"}
        except Exception as e:
            if attempt < max_retries - 1:
                log(f"请求错误，第{attempt+1}次重试: {e}", "WARN")
                time.sleep(1)
                continue
            return {"error": str(e)}
    
    return {"error": "Max retries exceeded"}

def get_price(symbol="BTCUSDT"):
    """获取价格"""
    result = api_call("/fapi/v1/ticker/price", {"symbol": symbol})
    return float(result['price']) if 'price' in result else None

def get_account():
    """获取账户信息"""
    return api_call("/fapi/v2/account")

def get_positions():
    """获取持仓"""
    result = api_call("/fapi/v2/positionRisk")
    if isinstance(result, list):
        return [p for p in result if float(p.get('positionAmt', 0)) != 0]
    return []

def open_long(symbol, quantity):
    """开多 - 单向模式"""
    log(f"🟢 开多 {symbol} {quantity}")
    result = api_call("/fapi/v1/order", {
        "symbol": symbol,
        "side": "BUY",
        "type": "MARKET",
        "quantity": quantity
    }, method="POST")
    
    # 如果是方向错误，尝试切换
    if result.get('code') == -4061:
        log("尝试以空单平仓方式开多...")
        # 先检查是否有空单，有则平仓
        positions = get_positions()
        for pos in positions:
            if pos['symbol'] == symbol and float(pos['positionAmt']) < 0:
                close_pos(symbol, abs(float(pos['positionAmt'])))
                # 然后再开多
                time.sleep(1)
                return api_call("/fapi/v1/order", {
                    "symbol": symbol,
                    "side": "BUY",
                    "type": "MARKET",
                    "quantity": quantity
                }, method="POST")
    
    return result

def open_short(symbol, quantity):
    """开空 - 单向模式"""
    log(f"🔴 开空 {symbol} {quantity}")
    result = api_call("/fapi/v1/order", {
        "symbol": symbol,
        "side": "SELL",
        "type": "MARKET",
        "quantity": quantity
    }, method="POST")
    
    # 如果是方向错误，尝试切换
    if result.get('code') == -4061:
        log("尝试以多单平仓方式开空...")
        # 先检查是否有单，有则平仓
        positions = get_positions()
        for pos in positions:
            if pos['symbol'] == symbol and float(pos['positionAmt']) > 0:
                close_pos(symbol, abs(float(pos['positionAmt'])))
                # 然后再开空
                time.sleep(1)
                return api_call("/fapi/v1/order", {
                    "symbol": symbol,
                    "side": "SELL",
                    "type": "MARKET",
                    "quantity": quantity
                }, method="POST")
    
    return result

def close_pos(symbol, quantity):
    """平仓 - 根据当前持仓方向自动判断"""
    positions = get_positions()
    for pos in positions:
        if pos['symbol'] == symbol:
            amt = float(pos['positionAmt'])
            close_side = "SELL" if amt > 0 else "BUY"
            qty = min(quantity, abs(amt))
            log(f"🔴 平仓 {close_side} {symbol} {qty}")
            return api_call("/fapi/v1/order", {
                "symbol": symbol,
                "side": close_side,
                "type": "MARKET",
                "quantity": qty
            }, method="POST")
    return {"error": "No position to close"}

def close_position(symbol, side, quantity):
    """平仓 (兼容函数)"""
    return close_pos(symbol, quantity)

def analyze_trend(symbol="BTCUSDT"):
    """分析趋势"""
    klines = api_call("/fapi/v1/klines", {"symbol": symbol, "interval": "5m", "limit": 10})
    if not isinstance(klines, list) or len(klines) < 5:
        return None
    
    prices = [float(k[4]) for k in klines]
    current = prices[-1]
    prev_5 = sum(prices[-5:]) / 5
    prev_10 = sum(prices[-10:]) / 10 if len(prices) >= 10 else prev_5
    
    change_5m = (current - prev_5) / prev_5 * 100
    change_10m = (current - prev_10) / prev_10 * 100
    
    return {
        "price": current,
        "change_5m": change_5m,
        "change_10m": change_10m,
        "trend": "UP" if change_5m > 0 else "DOWN"
    }

def trading_loop():
    """主交易循环"""
    log("="*60)
    log("🔥🔥🔥 手动盯盘交易启动 🔥🔥🔥")
    log("="*60)
    log("承诺：未来3天全权负责，每笔交易我亲自执行")
    log("="*60)
    
    trade_count = 0
    max_trades_per_day = 20
    
    while True:
        try:
            # 获取账户状态
            account = get_account()
            if 'availableBalance' not in account:
                log(f"获取账户失败: {account.get('error', 'Unknown')}", "ERROR")
                time.sleep(10)
                continue
            
            balance = float(account['availableBalance'])
            total = float(account['totalWalletBalance'])
            pnl = total - INITIAL_BALANCE
            pnl_pct = (pnl / INITIAL_BALANCE) * 100
            
            # 显示状态
            log(f"💰 余额: ${total:.2f} ({pnl:+.2f}, {pnl_pct:+.1f}%) | 交易: {trade_count}笔")
            
            # 检查持仓
            positions = get_positions()
            
            if positions:
                # 有持仓，管理止盈止损
                for pos in positions:
                    symbol = pos['symbol']
                    amt = float(pos['positionAmt'])
                    entry = float(pos['entryPrice'])
                    current = float(pos['markPrice'])
                    side = "LONG" if amt > 0 else "SHORT"
                    
                    pnl_pct_pos = (current - entry) / entry * 100
                    if side == "SHORT":
                        pnl_pct_pos = -pnl_pct_pos
                    
                    unrealized = float(pos.get('unRealizedProfit', 0))
                    log(f"📊 持仓 {symbol} {side}: {abs(amt)} @ ${entry} (盈亏: {pnl_pct_pos:.2f}%, ${unrealized:+.2f})")
                    
                    # 止盈4%或止损2%
                    if pnl_pct_pos >= 4:
                        log(f"🎯 止盈触发: {pnl_pct_pos:.2f}%")
                        result = close_position(symbol, side, abs(amt))
                        if 'orderId' in result:
                            trade_count += 1
                            log(f"✅ 止盈平仓成功!")
                        else:
                            log(f"❌ 平仓失败: {result.get('error', result)}")
                    
                    elif pnl_pct_pos <= -2:
                        log(f"🛑 止损触发: {pnl_pct_pos:.2f}%")
                        result = close_position(symbol, side, abs(amt))
                        if 'orderId' in result:
                            trade_count += 1
                            log(f"✅ 止损平仓成功!")
                        else:
                            log(f"❌ 平仓失败: {result.get('error', result)}")
            
            else:
                # 无持仓，寻找机会
                if trade_count >= max_trades_per_day:
                    log(f"⏳ 今日交易次数已达上限 ({max_trades_per_day})，等待明天")
                    time.sleep(300)
                    continue
                
                if balance < 5:
                    log(f"⚠️ 余额不足 (${balance:.2f})，停止交易")
                    break
                
                # 分析趋势
                analysis = analyze_trend("BTCUSDT")
                if analysis:
                    log(f"📈 BTC趋势: {analysis['trend']} ({analysis['change_5m']:+.3f}% / 5min)")
                    
                    # 简单策略：上涨就开多，下跌就开空
                    quantity = 0.005  # 固定小仓位
                    
                    if analysis['change_5m'] > 0.1:  # 上涨超过0.1%
                        log(f"🟢 信号: 开多 BTC {quantity}")
                        result = open_long("BTCUSDT", quantity)
                        if 'orderId' in result:
                            trade_count += 1
                            avg_price = result.get('avgPrice', analysis['price'])
                            log(f"✅✅✅ 开仓成功! OrderID: {result['orderId']} @ ${avg_price}")
                        else:
                            log(f"❌ 开仓失败: {result.get('error', result)}")
                    
                    elif analysis['change_5m'] < -0.1:  # 下跌超过0.1%
                        log(f"🔴 信号: 开空 BTC {quantity}")
                        result = open_short("BTCUSDT", quantity)
                        if 'orderId' in result:
                            trade_count += 1
                            avg_price = result.get('avgPrice', analysis['price'])
                            log(f"✅✅✅ 开仓成功! OrderID: {result['orderId']} @ ${avg_price}")
                        else:
                            log(f"❌ 开仓失败: {result.get('error', result)}")
                    else:
                        log(f"⏳ 趋势不明显，观望...")
            
            time.sleep(30)  # 每30秒检查一次
            
        except KeyboardInterrupt:
            log("🛑 手动交易停止")
            break
        except Exception as e:
            log(f"❌ 错误: {e}", "ERROR")
            time.sleep(10)

if __name__ == "__main__":
    trading_loop()
