#!/usr/bin/env python3
"""
全天候交易机器人 - 已修复版本
使用时间同步 + requests库
"""

import requests
import time
import json
import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import os
from datetime import datetime

# 配置
API_KEY = "Rzb1qhBd3BkIGLCO4rH7pTjPt1KZpq7lbgfIp0np81gOdq6xF9p7oFzqXq0cpLvs"
PRIVATE_KEY_B64 = "MC4CAQAwBQYDK2VwBCIEIISJgEmcDMko/bVi5n3nkDxNHpztDrqB08Ug5gGLDjdF"
DATA_DIR = os.path.expanduser("~/.openclaw/workspace/trading_data")
INITIAL_BALANCE = 50

# 初始化密钥
full_key = base64.b64decode(PRIVATE_KEY_B64)
seed = full_key[16:48]
private_key = Ed25519PrivateKey.from_private_bytes(seed)

# 交易参数
LEVERAGE = 10
STOP_LOSS_PCT = 0.02  # 2%
TAKE_PROFIT_PCT = 0.04  # 4%
TRADE_QTY = 0.002  # BTC数量

class BinanceTrader:
    def __init__(self):
        self.positions = {}
        self.trade_count = 0
        self.session = requests.Session()
        
    def log(self, msg, level="INFO"):
        ts = datetime.now().strftime('%H:%M:%S')
        line = f"[{ts}] [{level}] {msg}"
        print(line)
        with open(f"{DATA_DIR}/ACTIVE_TRADING.log", "a") as f:
            f.write(line + "\n")
    
    def get_server_time(self):
        """获取币安服务器时间"""
        try:
            resp = self.session.get("https://api.binance.com/api/v3/time", timeout=10)
            return resp.json()['serverTime']
        except:
            return int(time.time() * 1000)
    
    def api_call(self, endpoint, params, method="GET"):
        """API调用"""
        ts = self.get_server_time()
        params['timestamp'] = ts
        
        query = '&'.join([f"{k}={v}" for k, v in params.items()])
        sig = base64.b64encode(private_key.sign(query.encode('utf-8'))).decode('utf-8')
        
        headers = {'X-MBX-APIKEY': API_KEY}
        
        if method == "GET":
            url = f"https://fapi.binance.com{endpoint}?{query}&signature={sig}"
            r = self.session.get(url, headers=headers, timeout=20)
        else:
            url = f"https://fapi.binance.com{endpoint}"
            data = f"{query}&signature={sig}"
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            r = self.session.post(url, data=data, headers=headers, timeout=20)
        
        return r.json()
    
    def get_account(self):
        return self.api_call("/fapi/v2/account", {})
    
    def get_price(self, symbol="BTCUSDT"):
        result = self.api_call("/fapi/v1/ticker/price", {"symbol": symbol})
        return float(result['price']) if 'price' in result else None
    
    def get_positions(self):
        result = self.api_call("/fapi/v2/positionRisk", {})
        if isinstance(result, list):
            return [p for p in result if float(p.get('positionAmt', 0)) != 0]
        return []
    
    def open_long(self, symbol, quantity):
        self.log(f"🟢 开多 {symbol} {quantity}")
        return self.api_call("/fapi/v1/order", {
            "symbol": symbol,
            "side": "BUY",
            "positionSide": "LONG",
            "type": "MARKET",
            "quantity": quantity
        }, "POST")
    
    def close_long(self, symbol, quantity):
        self.log(f"🔴 平多 {symbol} {quantity}")
        return self.api_call("/fapi/v1/order", {
            "symbol": symbol,
            "side": "SELL",
            "positionSide": "LONG",
            "type": "MARKET",
            "quantity": quantity
        }, "POST")
    
    def analyze_trend(self):
        """简单趋势分析"""
        klines = self.api_call("/fapi/v1/klines", {"symbol": "BTCUSDT", "interval": "5m", "limit": 10})
        if not isinstance(klines, list) or len(klines) < 5:
            return None
        
        prices = [float(k[4]) for k in klines]
        recent = sum(prices[-3:]) / 3
        older = sum(prices[-6:-3]) / 3
        change = (recent - older) / older * 100
        
        return {
            "price": prices[-1],
            "change": change,
            "signal": "LONG" if change > 0.1 else "SHORT" if change < -0.1 else "HOLD"
        }
    
    def run(self):
        self.log("="*60)
        self.log("🔥🔥🔥 全天候交易机器人启动 🔥🔥🔥")
        self.log("="*60)
        self.log("✅ 已修复: 时间同步 + requests库")
        self.log("="*60)
        
        # 检查当前持仓
        positions = self.get_positions()
        if positions:
            self.log(f"📊 现有持仓: {len(positions)}个")
            for p in positions:
                self.log(f"   {p['symbol']}: {p['positionAmt']} @ ${p['entryPrice']}")
        else:
            self.log("📊 当前无持仓")
        
        while True:
            try:
                # 获取账户状态
                account = self.get_account()
                if 'totalWalletBalance' not in account:
                    self.log(f"获取账户失败", "ERROR")
                    time.sleep(10)
                    continue
                
                balance = float(account['totalWalletBalance'])
                pnl = balance - INITIAL_BALANCE
                pnl_pct = (pnl / INITIAL_BALANCE) * 100
                
                # 管理现有持仓
                positions = self.get_positions()
                
                if positions:
                    for pos in positions:
                        symbol = pos['symbol']
                        amt = float(pos['positionAmt'])
                        entry = float(pos['entryPrice'])
                        current = float(pos['markPrice'])
                        unrealized = float(pos.get('unRealizedProfit', 0))
                        
                        pnl_pct_pos = (current - entry) / entry * 100
                        
                        self.log(f"📊 {symbol} 持仓: {amt} @ ${entry} (盈亏: {pnl_pct_pos:.2f}%, ${unrealized:+.2f})")
                        
                        # 止盈止损
                        if pnl_pct_pos >= TAKE_PROFIT_PCT * 100:
                            self.log(f"🎯 止盈触发: {pnl_pct_pos:.2f}%")
                            result = self.close_long(symbol, abs(amt))
                            if 'orderId' in result:
                                self.log(f"✅ 止盈平仓成功!")
                                self.trade_count += 1
                        
                        elif pnl_pct_pos <= -STOP_LOSS_PCT * 100:
                            self.log(f"🛑 止损触发: {pnl_pct_pos:.2f}%")
                            result = self.close_long(symbol, abs(amt))
                            if 'orderId' in result:
                                self.log(f"✅ 止损平仓成功!")
                                self.trade_count += 1
                
                else:
                    # 无持仓，寻找机会
                    if balance < 5:
                        self.log(f"⚠️ 余额不足 (${balance:.2f})，停止交易")
                        break
                    
                    analysis = self.analyze_trend()
                    if analysis:
                        self.log(f"📈 趋势: {analysis['signal']} ({analysis['change']:+.3f}%) @ ${analysis['price']:,.2f}")
                        
                        if analysis['signal'] == "LONG":
                            result = self.open_long("BTCUSDT", TRADE_QTY)
                            if 'orderId' in result:
                                self.log(f"✅✅✅ 开仓成功! OrderID: {result['orderId']} @ ${result.get('avgPrice', 'N/A')}")
                                self.trade_count += 1
                            else:
                                self.log(f"❌ 开仓失败: {result.get('msg', result)}")
                
                # 显示总状态
                self.log(f"💰 总余额: ${balance:.2f} ({pnl:+.2f}, {pnl_pct:+.1f}%) | 交易: {self.trade_count}笔")
                
                time.sleep(30)  # 每30秒检查一次
                
            except KeyboardInterrupt:
                self.log("🛑 交易停止")
                break
            except Exception as e:
                self.log(f"❌ 错误: {e}", "ERROR")
                time.sleep(10)

if __name__ == "__main__":
    trader = BinanceTrader()
    trader.run()
