#!/usr/bin/env python3
"""
激进交易机器人 - 修复版
使用经过验证的API调用方式
"""

import time
import json
import base64
import csv
import os
import sys
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import urllib.request
import urllib.error

# ========== 激进配置 ==========
API_KEY = "Rzb1qhBd3BkIGLCO4rH7pTjPt1KZpq7lbgfIp0np81gOdq6xF9p7oFzqXq0cpLvs"
PRIVATE_KEY_B64 = "MC4CAQAwBQYDK2VwBCIEIISJgEmcDMko/bVi5n3nkDxNHpztDrqB08Ug5gGLDjdF"
DATA_DIR = os.path.expanduser("~/.openclaw/workspace/trading_data")

# 策略参数
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
LEVERAGE = 10
RISK_PER_TRADE = 0.20  # 20%
STOP_LOSS_PCT = 0.02   # 2%
TAKE_PROFIT_PCT = 0.04  # 4%
CHECK_INTERVAL = 30    # 30秒
INITIAL_BALANCE = 50

# 初始化密钥
full_key = base64.b64decode(PRIVATE_KEY_B64)
seed = full_key[16:48]
private_key = Ed25519PrivateKey.from_private_bytes(seed)

# ========== 工具函数 ==========
def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {msg}"
    print(log_line)
    with open(os.path.join(DATA_DIR, f"trades_{datetime.now().strftime('%Y%m%d')}.log"), "a") as f:
        f.write(log_line + "\n")

def get_server_time():
    """获取服务器时间，失败时使用本地时间+偏移"""
    try:
        req = urllib.request.Request("https://api.binance.com/api/v3/time")
        with urllib.request.urlopen(req, timeout=5) as resp:
            server_time = json.loads(resp.read().decode())['serverTime']
            local_time = int(time.time() * 1000)
            time_offset = server_time - local_time
            return local_time + time_offset
    except:
        return int(time.time() * 1000)

def api_request(endpoint, params=None, method="GET", base_url="https://fapi.binance.com"):
    """API请求 - 使用经过验证的方式"""
    timestamp = get_server_time()
    
    if params is None:
        params = {}
    params['timestamp'] = timestamp
    
    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    signature = private_key.sign(query_string.encode('utf-8'))
    sig_b64 = base64.b64encode(signature).decode('utf-8')
    
    if method == "GET":
        url = f"{base_url}{endpoint}?{query_string}&signature={sig_b64}"
        req = urllib.request.Request(url, headers={'X-MBX-APIKEY': API_KEY})
    else:
        url = f"{base_url}{endpoint}"
        data = f"{query_string}&signature={sig_b64}"
        req = urllib.request.Request(url, data=data.encode('utf-8'), 
                                     headers={'X-MBX-APIKEY': API_KEY, 
                                             'Content-Type': 'application/x-www-form-urlencoded'},
                                     method='POST')
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        err = json.loads(e.read().decode())
        return {"code": err.get('code'), "msg": err.get('msg')}
    except Exception as e:
        return {"error": str(e)}

# ========== 交易类 ==========
class AggressiveTrader:
    def __init__(self):
        self.price_history = {sym: [] for sym in SYMBOLS}
        self.positions = {}
        self.trade_count = 0
        
    def get_price(self, symbol):
        result = api_request("/fapi/v1/ticker/price", {"symbol": symbol})
        return float(result['price']) if 'price' in result else None
    
    def get_account(self):
        return api_request("/fapi/v2/account")
    
    def get_position(self, symbol):
        result = api_request("/fapi/v2/positionRisk", {"symbol": symbol})
        if isinstance(result, list):
            for pos in result:
                if pos['symbol'] == symbol and float(pos['positionAmt']) != 0:
                    return pos
        return None
    
    def analyze_trend(self, symbol):
        """简单趋势分析"""
        # 获取K线
        result = api_request("/fapi/v1/klines", {"symbol": symbol, "interval": "1m", "limit": 20})
        if not isinstance(result, list) or len(result) < 10:
            return None
        
        prices = [float(k[4]) for k in result]
        current_price = prices[-1]
        
        # 简单趋势判断
        if len(prices) < 10:
            return None
        
        recent_avg = sum(prices[-5:]) / 5
        older_avg = sum(prices[-10:-5]) / 5
        
        if recent_avg > older_avg * 1.002:  # 0.2%上涨趋势
            return {"signal": "LONG", "price": current_price, "strength": 3}
        elif recent_avg < older_avg * 0.998:  # 0.2%下跌趋势
            return {"signal": "SHORT", "price": current_price, "strength": 3}
        
        return None
    
    def calculate_quantity(self, price, stop_loss_pct):
        """计算仓位"""
        account = self.get_account()
        if 'availableBalance' not in account:
            log("无法获取余额", "ERROR")
            return 0
        
        balance = float(account['availableBalance'])
        if balance <= 0:
            return 0
        
        # 计算数量
        risk_usdt = balance * RISK_PER_TRADE
        position_value = risk_usdt / stop_loss_pct
        quantity = position_value / price
        
        # 限制最大数量
        quantity = min(quantity, 0.1)  # 最大0.1 BTC/ETH
        
        if quantity < 0.001:
            log(f"数量太小: {quantity}", "WARN")
            return 0
        
        log(f"仓位计算: 余额={balance:.2f}, 数量={quantity:.4f}, 价格=${price:.2f}")
        return round(quantity, 4)
    
    def open_trade(self, symbol, signal_info):
        """开仓 - 使用单向持仓模式"""
        side = "BUY" if signal_info["signal"] == "LONG" else "SELL"
        price = signal_info["price"]
        
        quantity = self.calculate_quantity(price, STOP_LOSS_PCT)
        if quantity <= 0:
            return False
        
        log(f"🟢【进攻】开仓 {side} {symbol} @ ${price:.2f}, 数量={quantity}")
        
        result = api_request("/fapi/v1/order", {
            "symbol": symbol,
            "side": side,
            "type": "MARKET",
            "quantity": quantity
            # 不指定positionSide，使用默认单向模式
        }, method="POST")
        
        if 'orderId' in result:
            avg_price = result.get('avgPrice', price)
            log(f"✅ 开仓成功! OrderID={result['orderId']}, 成交价=${avg_price}")
            self.positions[symbol] = {
                "side": signal_info["signal"],
                "entry": float(avg_price),
                "quantity": quantity
            }
            self.trade_count += 1
            return True
        else:
            log(f"❌ 开仓失败: {result.get('msg', result.get('error'))}", "ERROR")
            return False
    
    def close_trade(self, symbol, reason):
        """平仓 - 使用单向持仓模式"""
        pos = self.get_position(symbol)
        if not pos:
            return False
        
        amt = float(pos['positionAmt'])
        side = "SELL" if amt > 0 else "BUY"
        qty = abs(amt)
        
        log(f"🔴 平仓 {side} {symbol} | 原因: {reason}")
        
        result = api_request("/fapi/v1/order", {
            "symbol": symbol,
            "side": side,
            "type": "MARKET",
            "quantity": qty
            # 不指定positionSide，使用默认单向模式
        }, method="POST")
        
        if 'orderId' in result:
            pnl = float(pos.get('unRealizedProfit', 0))
            log(f"✅ 平仓成功! PnL=${pnl:+.2f}")
            if symbol in self.positions:
                del self.positions[symbol]
            return True
        return False
    
    def manage_positions(self):
        """管理持仓"""
        for symbol in list(self.positions.keys()):
            pos = self.get_position(symbol)
            if not pos:
                continue
            
            entry = float(pos['entryPrice'])
            current = float(pos['markPrice'])
            amt = float(pos['positionAmt'])
            
            pnl_pct = (current - entry) / entry * 100
            if amt < 0:
                pnl_pct = -pnl_pct
            
            # 止盈
            if pnl_pct >= TAKE_PROFIT_PCT * 100:
                self.close_trade(symbol, f"止盈 {pnl_pct:.2f}%")
            # 止损
            elif pnl_pct <= -STOP_LOSS_PCT * 100:
                self.close_trade(symbol, f"止损 {pnl_pct:.2f}%")
    
    def run(self):
        log("="*60)
        log("🔥🔥🔥 激进进攻机器人 V3.0 🔥🔥🔥")
        log("="*60)
        log("策略: 高频交易 + 2%止损/4%止盈")
        log("目标: 3天盈利50% (不赚钱就是亏!)")
        log("="*60)
        
        while True:
            try:
                # 管理现有持仓
                self.manage_positions()
                
                # 检查已有持仓数量
                if len(self.positions) >= 2:
                    time.sleep(CHECK_INTERVAL)
                    continue
                
                # 寻找交易机会
                for symbol in SYMBOLS:
                    if symbol in self.positions:
                        continue
                    
                    signal = self.analyze_trend(symbol)
                    if signal:
                        log(f"📊 {symbol} 信号: {signal['signal']} (强度:{signal['strength']})")
                        self.open_trade(symbol, signal)
                        break  # 一次只开一个
                
                # 显示状态
                account = self.get_account()
                if 'totalWalletBalance' in account:
                    balance = float(account['totalWalletBalance'])
                    pnl = balance - INITIAL_BALANCE
                    pnl_pct = (pnl / INITIAL_BALANCE) * 100
                    log(f"💰 余额: ${balance:.2f} ({pnl:+.2f}USDT, {pnl_pct:+.1f}%) | 交易: {self.trade_count}笔")
                
                time.sleep(CHECK_INTERVAL)
                
            except KeyboardInterrupt:
                log("🛑 停止交易")
                break
            except Exception as e:
                log(f"❌ 错误: {e}", "ERROR")
                time.sleep(10)

if __name__ == "__main__":
    trader = AggressiveTrader()
    trader.run()
