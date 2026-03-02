#!/usr/bin/env python3
"""
🛡️ 稳健盈利交易机器人 v2.0
策略: 趋势跟随 + 严格风控
目标: 从$50稳健增长到$75（50%盈利）
"""

import requests
import time
import json
import base64
import hmac
import hashlib
from datetime import datetime, timedelta
import os
import sys

# ============ 配置 ============
CONFIG = {
    "api_key": "Rzb1qhBd3BkIGLCO4rH7pTjPt1KZpq7lbgfIp0np81gOdq6xF9p7oFzqXq0cpLvs",
    "private_key_b64": "MC4CAQAwBQYDK2VwBCIEIISJgEmcDMko/bVi5n3nkDxNHpztDrqB08Ug5gGLDjdF",
    
    # 交易参数
    "initial_balance": 49.57,  # 当前可用资金
    "target_balance": 75.00,    # 目标盈利50%
    "risk_per_trade": 0.02,     # 单笔风险2%
    "max_daily_loss": 0.05,     # 日最大亏损5%
    "max_trades_per_day": 5,    # 日最大交易次数
    "max_positions": 2,         # 最大同时持仓
    
    # 策略参数
    "symbols": ["BTCUSDT", "ETHUSDT"],  # 交易币种
    "timeframe": "1h",          # 主周期
    "ema_fast": 20,
    "ema_slow": 50,
    "rsi_period": 14,
    "atr_period": 14,
    
    # 风控参数
    "leverage": 1,              # 现货交易，1倍杠杆
    "stop_loss_atr": 1.5,       # 止损 = 1.5 * ATR
    "take_profit_atr": 3.0,     # 止盈 = 3 * ATR
}

DATA_DIR = os.path.expanduser("~/.openclaw/workspace/trading_data")
LOG_FILE = f"{DATA_DIR}/SAFE_TRADING.log"
POSITION_FILE = f"{DATA_DIR}/positions.json"
DAILY_STATS_FILE = f"{DATA_DIR}/daily_stats.json"

# ============ 工具函数 ============
def log(msg, level="INFO"):
    """记录日志"""
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def send_alert(title, message, priority="normal"):
    """发送报警（可扩展到飞书/邮件）"""
    log(f"🚨 ALERT [{priority}]: {title} - {message}", "ALERT")
    # TODO: 集成飞书通知

def get_server_time():
    """获取币安服务器时间"""
    try:
        resp = requests.get("https://api.binance.com/api/v3/time", timeout=10)
        return resp.json()['serverTime']
    except Exception as e:
        log(f"获取服务器时间失败: {e}", "ERROR")
        return int(time.time() * 1000)

# ============ Ed25519 签名 ============
def sign_request(params):
    """使用Ed25519签名"""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    
    private_key_b64 = CONFIG["private_key_b64"]
    full_key = base64.b64decode(private_key_b64)
    seed = full_key[16:48]
    private_key = Ed25519PrivateKey.from_private_bytes(seed)
    
    query = '&'.join([f"{k}={v}" for k, v in params.items()])
    signature = private_key.sign(query.encode('utf-8'))
    return base64.b64encode(signature).decode('utf-8')

# ============ API 调用 ============
class BinanceAPI:
    def __init__(self):
        self.api_key = CONFIG["api_key"]
        self.base_url = "https://api.binance.com"
        self.session = requests.Session()
        self.session.headers.update({'X-MBX-APIKEY': self.api_key})
    
    def _make_request(self, endpoint, params=None, method="GET"):
        """发起签名请求"""
        if params is None:
            params = {}
        
        ts = get_server_time()
        params['timestamp'] = ts
        
        query = '&'.join([f"{k}={v}" for k, v in params.items()])
        signature = sign_request(params)
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                full_url = f"{url}?{query}&signature={signature}"
                resp = self.session.get(full_url, timeout=20)
            else:
                data = f"{query}&signature={signature}"
                resp = self.session.post(url, data=data, timeout=20)
            
            if resp.status_code == 200:
                return resp.json()
            else:
                log(f"API错误: {resp.status_code} - {resp.text}", "ERROR")
                return None
        except Exception as e:
            log(f"请求异常: {e}", "ERROR")
            return None
    
    def get_account(self):
        """获取账户信息"""
        return self._make_request("/api/v3/account")
    
    def get_balance(self, asset):
        """获取指定资产余额"""
        account = self.get_account()
        if account and 'balances' in account:
            for balance in account['balances']:
                if balance['asset'] == asset:
                    return float(balance['free'])
        return 0.0
    
    def get_klines(self, symbol, interval, limit=100):
        """获取K线数据"""
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        try:
            resp = requests.get(f"{self.base_url}/api/v3/klines", params=params, timeout=10)
            if resp.status_code == 200:
                # 转换K线格式: [timestamp, open, high, low, close, volume, ...]
                data = resp.json()
                return {
                    'timestamp': [k[0] for k in data],
                    'open': [float(k[1]) for k in data],
                    'high': [float(k[2]) for k in data],
                    'low': [float(k[3]) for k in data],
                    'close': [float(k[4]) for k in data],
                    'volume': [float(k[5]) for k in data]
                }
            return None
        except Exception as e:
            log(f"获取K线失败: {e}", "ERROR")
            return None
    
    def get_ticker(self, symbol):
        """获取最新价格"""
        try:
            resp = requests.get(f"{self.base_url}/api/v3/ticker/price", 
                              params={'symbol': symbol}, timeout=10)
            if resp.status_code == 200:
                return float(resp.json()['price'])
            return None
        except:
            return None
    
    def place_order(self, symbol, side, quantity, order_type="MARKET"):
        """下单"""
        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': quantity
        }
        return self._make_request("/api/v3/order", params, "POST")

# ============ 技术指标 ============
class TechnicalAnalysis:
    @staticmethod
    def calculate_ema(prices, period):
        """计算EMA"""
        if len(prices) < period:
            return None
        
        multiplier = 2 / (period + 1)
        ema = [sum(prices[:period]) / period]  # 初始SMA
        
        for price in prices[period:]:
            ema.append((price - ema[-1]) * multiplier + ema[-1])
        
        return ema
    
    @staticmethod
    def calculate_rsi(prices, period=14):
        """计算RSI"""
        if len(prices) < period + 1:
            return None
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        rsi_values = []
        for i in range(period, len(gains)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            rsi_values.append(rsi)
        
        return rsi_values[-1] if rsi_values else None
    
    @staticmethod
    def calculate_atr(highs, lows, closes, period=14):
        """计算ATR"""
        if len(closes) < period + 1:
            return None
        
        tr_values = []
        for i in range(1, len(closes)):
            tr1 = highs[i] - lows[i]
            tr2 = abs(highs[i] - closes[i-1])
            tr3 = abs(lows[i] - closes[i-1])
            tr_values.append(max(tr1, tr2, tr3))
        
        atr = sum(tr_values[:period]) / period
        for i in range(period, len(tr_values)):
            atr = (atr * (period - 1) + tr_values[i]) / period
        
        return atr
    
    @staticmethod
    def calculate_adx(highs, lows, closes, period=14):
        """计算ADX（趋势强度）"""
        # 简化版ADX计算
        if len(closes) < period * 2:
            return None
        
        plus_dm = []
        minus_dm = []
        tr_values = []
        
        for i in range(1, len(closes)):
            plus = highs[i] - highs[i-1]
            minus = lows[i-1] - lows[i]
            
            plus_dm.append(plus if plus > minus and plus > 0 else 0)
            minus_dm.append(minus if minus > plus and minus > 0 else 0)
            
            tr1 = highs[i] - lows[i]
            tr2 = abs(highs[i] - closes[i-1])
            tr3 = abs(lows[i] - closes[i-1])
            tr_values.append(max(tr1, tr2, tr3))
        
        # 平滑处理
        atr = sum(tr_values[:period]) / period
        plus_di = 100 * sum(plus_dm[:period]) / (period * atr) if atr > 0 else 0
        minus_di = 100 * sum(minus_dm[:period]) / (period * atr) if atr > 0 else 0
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di) if (plus_di + minus_di) > 0 else 0
        return dx

# ============ 仓位管理 ============
class PositionManager:
    def __init__(self):
        self.positions = self.load_positions()
        self.daily_stats = self.load_daily_stats()
    
    def load_positions(self):
        """加载持仓"""
        if os.path.exists(POSITION_FILE):
            with open(POSITION_FILE, 'r') as f:
                return json.load(f)
        return {}
    
    def save_positions(self):
        """保存持仓"""
        with open(POSITION_FILE, 'w') as f:
            json.dump(self.positions, f, indent=2)
    
    def load_daily_stats(self):
        """加载每日统计"""
        today = datetime.now().strftime('%Y-%m-%d')
        if os.path.exists(DAILY_STATS_FILE):
            with open(DAILY_STATS_FILE, 'r') as f:
                stats = json.load(f)
                if stats.get('date') == today:
                    return stats
        
        return {
            'date': today,
            'trades': 0,
            'wins': 0,
            'losses': 0,
            'pnl': 0,
            'max_drawdown': 0
        }
    
    def save_daily_stats(self):
        """保存每日统计"""
        with open(DAILY_STATS_FILE, 'w') as f:
            json.dump(self.daily_stats, f, indent=2)
    
    def can_trade(self, balance):
        """检查是否可以交易"""
        # 检查日交易次数
        if self.daily_stats['trades'] >= CONFIG['max_trades_per_day']:
            log(f"已达日最大交易次数: {CONFIG['max_trades_per_day']}", "WARN")
            return False
        
        # 检查日亏损
        day_loss_pct = abs(self.daily_stats['pnl']) / CONFIG['initial_balance']
        if day_loss_pct >= CONFIG['max_daily_loss']:
            log(f"已达日最大亏损: -{day_loss_pct*100:.1f}%", "WARN")
            send_alert("日亏损限制", f"今日亏损已达{day_loss_pct*100:.1f}%，停止交易")
            return False
        
        # 检查持仓数量
        if len(self.positions) >= CONFIG['max_positions']:
            log(f"已达最大持仓数: {CONFIG['max_positions']}", "WARN")
            return False
        
        return True
    
    def calculate_position_size(self, balance, entry_price, stop_price):
        """计算仓位大小"""
        risk_amount = balance * CONFIG['risk_per_trade']  # 风险金额
        price_diff = abs(entry_price - stop_price)
        
        if price_diff == 0:
            return 0
        
        # 计算数量
        quantity = risk_amount / price_diff
        
        # 限制名义价值（1倍杠杆 = 不杠杆）
        max_notional = balance * CONFIG['leverage']
        if quantity * entry_price > max_notional:
            quantity = max_notional / entry_price
        
        # 根据币种调整精度
        if quantity < 0.0001:
            quantity = 0.0001
        
        return round(quantity, 6)
    
    def add_position(self, symbol, side, entry_price, stop_price, take_profit, quantity):
        """添加持仓"""
        self.positions[symbol] = {
            'side': side,
            'entry_price': entry_price,
            'stop_price': stop_price,
            'take_profit': take_profit,
            'quantity': quantity,
            'entry_time': datetime.now().isoformat(),
            'highest_price': entry_price if side == 'LONG' else entry_price,
            'lowest_price': entry_price if side == 'SHORT' else entry_price
        }
        self.save_positions()
        
        self.daily_stats['trades'] += 1
        self.save_daily_stats()
    
    def remove_position(self, symbol, exit_price, pnl):
        """移除持仓"""
        if symbol in self.positions:
            del self.positions[symbol]
            self.save_positions()
            
            self.daily_stats['pnl'] += pnl
            if pnl > 0:
                self.daily_stats['wins'] += 1
            else:
                self.daily_stats['losses'] += 1
            self.save_daily_stats()

# ============ 策略 ============
class TrendFollowStrategy:
    """趋势跟随策略"""
    
    def __init__(self, api: BinanceAPI):
        self.api = api
        self.ta = TechnicalAnalysis()
    
    def analyze(self, symbol):
        """分析交易信号"""
        # 获取K线数据
        klines = self.api.get_klines(symbol, CONFIG['timeframe'], limit=100)
        if not klines:
            return None
        
        closes = klines['close']
        highs = klines['high']
        lows = klines['low']
        
        # 计算指标
        ema20 = self.ta.calculate_ema(closes, CONFIG['ema_fast'])
        ema50 = self.ta.calculate_ema(closes, CONFIG['ema_slow'])
        rsi = self.ta.calculate_rsi(closes, CONFIG['rsi_period'])
        atr = self.ta.calculate_atr(highs, lows, closes, CONFIG['atr_period'])
        adx = self.ta.calculate_adx(highs, lows, closes, 14)
        
        if not all([ema20, ema50, rsi, atr, adx]):
            return None
        
        current_price = closes[-1]
        prev_price = closes[-2]
        
        result = {
            'symbol': symbol,
            'price': current_price,
            'ema20': ema20[-1],
            'ema50': ema50[-1],
            'rsi': rsi,
            'atr': atr,
            'adx': adx,
            'signal': None,
            'stop_loss': None,
            'take_profit': None
        }
        
        # 趋势判断
        uptrend = current_price > ema20[-1] > ema50[-1]
        downtrend = current_price < ema20[-1] < ema50[-1]
        
        # 只在强趋势中交易
        if adx < 20:
            result['note'] = f"趋势太弱 (ADX={adx:.1f})，观望"
            return result
        
        # 多头信号
        if uptrend and rsi < 60 and rsi > 40:
            # RSI从低位回升确认
            prev_rsi = self.ta.calculate_rsi(closes[:-1], CONFIG['rsi_period'])
            if prev_rsi and rsi > prev_rsi:
                result['signal'] = 'LONG'
                result['stop_loss'] = current_price - CONFIG['stop_loss_atr'] * atr
                result['take_profit'] = current_price + CONFIG['take_profit_atr'] * atr
        
        # 空头信号
        elif downtrend and rsi > 40 and rsi < 60:
            # RSI从高位回落确认
            prev_rsi = self.ta.calculate_rsi(closes[:-1], CONFIG['rsi_period'])
            if prev_rsi and rsi < prev_rsi:
                result['signal'] = 'SHORT'
                result['stop_loss'] = current_price + CONFIG['stop_loss_atr'] * atr
                result['take_profit'] = current_price - CONFIG['take_profit_atr'] * atr
        
        return result

# ============ 交易机器人 ============
class SafeTradingBot:
    def __init__(self):
        self.api = BinanceAPI()
        self.position_mgr = PositionManager()
        self.strategy = TrendFollowStrategy(self.api)
        self.running = True
        
        log("="*60)
        log("🛡️ 稳健盈利交易机器人 v2.0 启动")
        log("="*60)
        log(f"💰 初始资金: ${CONFIG['initial_balance']:.2f}")
        log(f"🎯 目标资金: ${CONFIG['target_balance']:.2f}")
        log(f"⚠️  单笔风险: {CONFIG['risk_per_trade']*100}%")
        log(f"📊 交易周期: {CONFIG['timeframe']}")
        log("="*60)
    
    def check_account(self):
        """检查账户状态"""
        account = self.api.get_account()
        if not account:
            log("无法获取账户信息", "ERROR")
            return None
        
        # 计算总余额
        total_usdt = 0
        for balance in account['balances']:
            asset = balance['asset']
            free = float(balance['free'])
            locked = float(balance['locked'])
            
            if asset == 'USDT':
                total_usdt += free + locked
            elif free > 0:
                # 获取价格并计算USDT价值
                price = self.api.get_ticker(f"{asset}USDT")
                if price:
                    total_usdt += (free + locked) * price
        
        return total_usdt
    
    def monitor_positions(self):
        """监控持仓，检查止损止盈"""
        for symbol, pos in list(self.position_mgr.positions.items()):
            current_price = self.api.get_ticker(symbol)
            if not current_price:
                continue
            
            entry = pos['entry_price']
            stop = pos['stop_price']
            target = pos['take_profit']
            quantity = pos['quantity']
            side = pos['side']
            
            # 计算盈亏
            if side == 'LONG':
                pnl = (current_price - entry) * quantity
                pnl_pct = (current_price - entry) / entry * 100
                
                # 更新最高价（移动止损用）
                if current_price > pos.get('highest_price', entry):
                    pos['highest_price'] = current_price
                    self.position_mgr.save_positions()
                
                # 检查止损
                if current_price <= stop:
                    log(f"🔴 止损触发 {symbol}: ${current_price:.2f} (亏损 {pnl_pct:.2f}%)")
                    self.close_position(symbol, current_price, pnl)
                    continue
                
                # 检查止盈
                if current_price >= target:
                    log(f"🟢 止盈触发 {symbol}: ${current_price:.2f} (盈利 {pnl_pct:.2f}%)")
                    self.close_position(symbol, current_price, pnl)
                    continue
                
                # 移动止损（保本）
                if current_price >= entry * 1.02:  # 盈利2%后
                    new_stop = entry * 1.005  # 保本
                    if new_stop > stop:
                        pos['stop_price'] = new_stop
                        self.position_mgr.save_positions()
                        log(f"📈 {symbol} 移动止损至保本价: ${new_stop:.2f}")
            
            else:  # SHORT
                pnl = (entry - current_price) * quantity
                pnl_pct = (entry - current_price) / entry * 100
                
                # 更新最低价
                if current_price < pos.get('lowest_price', entry):
                    pos['lowest_price'] = current_price
                    self.position_mgr.save_positions()
                
                # 检查止损
                if current_price >= stop:
                    log(f"🔴 止损触发 {symbol}: ${current_price:.2f} (亏损 {pnl_pct:.2f}%)")
                    self.close_position(symbol, current_price, pnl)
                    continue
                
                # 检查止盈
                if current_price <= target:
                    log(f"🟢 止盈触发 {symbol}: ${current_price:.2f} (盈利 {pnl_pct:.2f}%)")
                    self.close_position(symbol, current_price, pnl)
                    continue
                
                # 移动止损
                if current_price <= entry * 0.98:
                    new_stop = entry * 0.995
                    if new_stop < stop:
                        pos['stop_price'] = new_stop
                        self.position_mgr.save_positions()
                        log(f"📉 {symbol} 移动止损至保本价: ${new_stop:.2f}")
    
    def close_position(self, symbol, exit_price, pnl):
        """平仓"""
        pos = self.position_mgr.positions.get(symbol)
        if not pos:
            return
        
        side = 'SELL' if pos['side'] == 'LONG' else 'BUY'
        quantity = pos['quantity']
        
        # 执行平仓（现货交易）
        if pos['side'] == 'LONG':
            # 卖出BTC
            result = self.api.place_order(symbol, 'SELL', quantity)
        else:
            # 买入BTC（需要先有USDT）
            result = self.api.place_order(symbol, 'BUY', quantity)
        
        if result:
            log(f"✅ 平仓成功 {symbol}: {side} {quantity} @ ${exit_price:.2f}")
            self.position_mgr.remove_position(symbol, exit_price, pnl)
            
            if pnl > 0:
                log(f"💰 盈利: +${pnl:.2f} 🎉")
            else:
                log(f"💸 亏损: ${pnl:.2f}")
        else:
            log(f"❌ 平仓失败 {symbol}", "ERROR")
    
    def open_position(self, symbol, signal, price, stop, target):
        """开仓"""
        balance = self.check_account()
        if not balance:
            return
        
        # 检查是否可以交易
        if not self.position_mgr.can_trade(balance):
            return
        
        # 计算仓位
        quantity = self.position_mgr.calculate_position_size(balance, price, stop)
        if quantity <= 0:
            log(f"仓位计算为0，跳过 {symbol}", "WARN")
            return
        
        side = 'BUY' if signal == 'LONG' else 'SELL'
        
        # 检查余额
        if signal == 'LONG':
            usdt_needed = quantity * price
            usdt_balance = self.api.get_balance('USDT')
            if usdt_balance < usdt_needed:
                log(f"USDT余额不足: {usdt_balance:.2f} < {usdt_needed:.2f}", "WARN")
                return
        else:
            # SHORT现货需要借币，暂时不支持
            log("SHORT信号但现货不支持做空，跳过", "WARN")
            return
        
        # 执行开仓
        result = self.api.place_order(symbol, side, quantity)
        
        if result:
            log(f"✅ 开仓成功 {symbol}: {signal} {quantity} @ ${price:.2f}")
            log(f"   止损: ${stop:.2f}, 止盈: ${target:.2f}")
            
            self.position_mgr.add_position(symbol, signal, price, stop, target, quantity)
        else:
            log(f"❌ 开仓失败 {symbol}", "ERROR")
    
    def scan_signals(self):
        """扫描交易信号"""
        for symbol in CONFIG['symbols']:
            # 已有持仓则跳过
            if symbol in self.position_mgr.positions:
                continue
            
            result = self.strategy.analyze(symbol)
            if not result:
                continue
            
            log(f"📊 {symbol}: 价格=${result['price']:.2f}, EMA20={result['ema20']:.2f}, "
                f"RSI={result['rsi']:.1f}, ADX={result['adx']:.1f}")
            
            if result.get('signal'):
                log(f"🎯 信号: {result['signal']} {symbol}")
                self.open_position(
                    symbol,
                    result['signal'],
                    result['price'],
                    result['stop_loss'],
                    result['take_profit']
                )
            elif result.get('note'):
                log(f"⏳ {result['note']}")
    
    def print_status(self):
        """打印状态"""
        balance = self.check_account()
        if not balance:
            return
        
        pnl = balance - CONFIG['initial_balance']
        pnl_pct = pnl / CONFIG['initial_balance'] * 100
        
        log("="*60)
        log(f"💰 当前余额: ${balance:.2f} ({pnl:+.2f}, {pnl_pct:+.1f}%)")
        log(f"🎯 目标进度: {balance/CONFIG['target_balance']*100:.1f}%")
        log(f"📊 今日交易: {self.position_mgr.daily_stats['trades']}笔")
        log(f"   今日盈亏: ${self.position_mgr.daily_stats['pnl']:+.2f}")
        log(f"📈 持仓: {len(self.position_mgr.positions)}个")
        
        for symbol, pos in self.position_mgr.positions.items():
            current = self.api.get_ticker(symbol)
            if current:
                if pos['side'] == 'LONG':
                    pnl = (current - pos['entry_price']) * pos['quantity']
                else:
                    pnl = (pos['entry_price'] - current) * pos['quantity']
                log(f"   {symbol} {pos['side']}: ${pnl:+.2f}")
        
        log("="*60)
    
    def run(self):
        """主循环"""
        log("开始交易循环...")
        
        while self.running:
            try:
                # 1. 监控现有持仓
                self.monitor_positions()
                
                # 2. 扫描新信号
                self.scan_signals()
                
                # 3. 打印状态
                self.print_status()
                
                # 4. 等待下一个周期
                log(f"等待5分钟后继续...")
                time.sleep(300)  # 5分钟
                
            except KeyboardInterrupt:
                log("收到停止信号，正在退出...")
                self.running = False
            except Exception as e:
                log(f"主循环异常: {e}", "ERROR")
                time.sleep(60)

# ============ 启动 ============
if __name__ == "__main__":
    bot = SafeTradingBot()
    bot.run()
