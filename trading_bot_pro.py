#!/usr/bin/env python3
"""
专业操盘手策略 - 3天50%盈利目标
V2.0 - 多维度信号 + 智能风控 + 波动率适应
"""

import time
import json
import base64
import csv
import os
import sys
import statistics
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import urllib.request

# ========== 激进进攻配置 ==========
CONFIG = {
    "api_key": "Rzb1qhBd3BkIGLCO4rH7pTjPt1KZpq7lbgfIp0np81gOdq6xF9p7oFzqXq0cpLvs",
    "private_key_b64": "MC4CAQAwBQYDK2VwBCIEIISJgEmcDMko/bVi5n3nkDxNHpztDrqB08Ug5gGLDjdF",
    "symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT"],  # 多币种监控
    "primary_symbol": "BTCUSDT",  # 主交易对
    "check_interval": 30,  # 30秒高频监控
    "target_profit": 0.50,
    "initial_balance": 50,
    "max_daily_loss": 15,  # 允许亏损15 USDT (30%)
    "leverage": 10,  # 10倍杠杆
    
    # 进攻参数 - 降低门槛
    "trend_lookback": 10,  # 10周期趋势 (更敏感)
    "rsi_period": 14,
    "rsi_overbought": 75,  # 放宽超买
    "rsi_oversold": 25,    # 放宽超卖
    "atr_period": 14,
    "adx_threshold": 15,   # ADX > 15 即可 (降低趋势要求)
    "volume_ma_period": 20,
    "require_volume_spike": False,  # 不强制要求放量
    
    # 激进风控 - 提高仓位
    "risk_per_trade": 0.20,  # 单笔风险20% (!!!)
    "min_risk_reward": 2.0,  # 2:1盈亏比即可
    "max_positions": 3,  # 最多3个同时持仓
    "cooldown_after_loss": 60,   # 亏损后仅冷却1分钟
    "cooldown_after_win": 30,    # 盈利后仅冷却30秒
    
    # 止盈止损 - 更快进出
    "take_profit_pct": 0.04,     # 4%止盈 (更快锁定利润)
    "stop_loss_pct": 0.02,       # 2%止损
    "trailing_stop": 0.015,      # 1.5%追踪止损
    "use_trailing": True,        # 启用追踪止盈
    
    "data_dir": os.path.expanduser("~/.openclaw/workspace/trading_data"),
}

# 初始化密钥
full_key = base64.b64decode(CONFIG["private_key_b64"])
seed = full_key[16:48]
PRIVATE_KEY = Ed25519PrivateKey.from_private_bytes(seed)

# ========== 专业工具函数 ==========
def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {msg}"
    print(log_line)
    log_file = os.path.join(CONFIG["data_dir"], f"trades_{datetime.now().strftime('%Y%m%d')}.log")
    with open(log_file, "a") as f:
        f.write(log_line + "\n")

def get_server_time():
    """获取币安服务器时间"""
    try:
        req = urllib.request.Request("https://api.binance.com/api/v3/time")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())['serverTime']
    except:
        return int(time.time() * 1000)

def make_request(endpoint, params=None, base_url="https://fapi.binance.com"):
    """发送GET请求"""
    server_time = get_server_time()
    
    if params is None:
        params = {}
    params['timestamp'] = server_time
    
    # 构建query string
    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    
    # Ed25519签名
    signature = PRIVATE_KEY.sign(query_string.encode('utf-8'))
    sig_b64 = base64.b64encode(signature).decode('utf-8')
    
    url = f"{base_url}{endpoint}?{query_string}&signature={sig_b64}"
    
    req = urllib.request.Request(url, headers={'X-MBX-APIKEY': CONFIG["api_key"]})
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        try:
            err_json = json.loads(err_body)
            log(f"API错误: {err_json.get('code')} - {err_json.get('msg')}", "ERROR")
            return err_json
        except:
            return {"error": err_body[:200]}
    except Exception as e:
        log(f"请求错误: {e}", "ERROR")
        return {"error": str(e)}

def make_post_request(endpoint, params, base_url="https://fapi.binance.com"):
    """发送POST请求"""
    server_time = get_server_time()
    
    params['timestamp'] = server_time
    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    
    # Ed25519签名
    signature = PRIVATE_KEY.sign(query_string.encode('utf-8'))
    sig_b64 = base64.b64encode(signature).decode('utf-8')
    
    url = f"{base_url}{endpoint}"
    data = f"{query_string}&signature={sig_b64}"
    
    req = urllib.request.Request(url, data=data.encode('utf-8'), headers={
        'X-MBX-APIKEY': CONFIG["api_key"],
        'Content-Type': 'application/x-www-form-urlencoded'
    }, method='POST')
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        try:
            err_json = json.loads(err_body)
            log(f"API错误: {err_json.get('code')} - {err_json.get('msg')}", "ERROR")
            return err_json
        except:
            return {"error": err_body[:200]}
    except Exception as e:
        log(f"请求错误: {e}", "ERROR")
        return {"error": str(e)}

# ========== 专业技术指标 ==========
class TechnicalAnalysis:
    @staticmethod
    def calculate_sma(prices, period):
        """简单移动平均"""
        if len(prices) < period:
            return None
        return sum(prices[-period:]) / period
    
    @staticmethod
    def calculate_ema(prices, period):
        """指数移动平均"""
        if len(prices) < period:
            return None
        multiplier = 2 / (period + 1)
        ema = prices[0]
        for price in prices[1:]:
            ema = (price - ema) * multiplier + ema
        return ema
    
    @staticmethod
    def calculate_rsi(prices, period=14):
        """RSI相对强弱指数"""
        if len(prices) < period + 1:
            return 50
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        if len(gains) < period:
            return 50
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_atr(highs, lows, closes, period=14):
        """平均真实波幅 (Average True Range)"""
        if len(closes) < period + 1:
            return 0
        
        tr_list = []
        for i in range(1, len(closes)):
            tr1 = highs[i] - lows[i]
            tr2 = abs(highs[i] - closes[i-1])
            tr3 = abs(lows[i] - closes[i-1])
            tr_list.append(max(tr1, tr2, tr3))
        
        if len(tr_list) < period:
            return sum(tr_list) / len(tr_list) if tr_list else 0
        
        return sum(tr_list[-period:]) / period
    
    @staticmethod
    def calculate_adx(highs, lows, closes, period=14):
        """ADX平均趋向指数 (判断趋势强度)"""
        if len(closes) < period * 2:
            return 0
        
        # 简化版ADX计算
        plus_dm = []
        minus_dm = []
        tr_list = []
        
        for i in range(1, len(closes)):
            plus_dm.append(max(0, highs[i] - highs[i-1]))
            minus_dm.append(max(0, lows[i-1] - lows[i]))
            tr_list.append(max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1])))
        
        if len(tr_list) < period:
            return 0
        
        # 简化处理，实际ADX更复杂
        avg_plus_dm = sum(plus_dm[-period:]) / period
        avg_minus_dm = sum(minus_dm[-period:]) / period
        avg_tr = sum(tr_list[-period:]) / period
        
        if avg_tr == 0:
            return 0
        
        plus_di = 100 * avg_plus_dm / avg_tr
        minus_di = 100 * avg_minus_dm / avg_tr
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di) if (plus_di + minus_di) > 0 else 0
        return dx
    
    @staticmethod
    def calculate_bollinger_bands(prices, period=20, std_dev=2):
        """布林带"""
        if len(prices) < period:
            return None, None, None
        
        sma = sum(prices[-period:]) / period
        variance = sum([(p - sma) ** 2 for p in prices[-period:]]) / period
        std = variance ** 0.5
        
        upper = sma + (std_dev * std)
        lower = sma - (std_dev * std)
        
        return upper, sma, lower

# ========== 专业交易机器人 ==========
class ProTradingBot:
    def __init__(self):
        self.price_data = {sym: {"prices": [], "highs": [], "lows": [], "volumes": []} for sym in CONFIG["symbols"]}
        self.positions = {}  # 当前持仓
        self.daily_stats = {"wins": 0, "losses": 0, "pnl": 0}
        self.consecutive_losses = 0
        self.last_trade_time = 0
        self.cooldown_until = 0
        self.total_trades = 0
        
    def fetch_klines(self, symbol, interval="1m", limit=100):
        """获取K线数据"""
        result = make_request("/fapi/v1/klines", {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        })
        
        if isinstance(result, list):
            return result
        return []
    
    def update_market_data(self):
        """更新市场数据"""
        for symbol in CONFIG["symbols"]:
            klines = self.fetch_klines(symbol, "1m", 100)
            if klines:
                self.price_data[symbol]["prices"] = [float(k[4]) for k in klines]  # 收盘价
                self.price_data[symbol]["highs"] = [float(k[2]) for k in klines]  # 最高价
                self.price_data[symbol]["lows"] = [float(k[3]) for k in klines]   # 最低价
                self.price_data[symbol]["volumes"] = [float(k[5]) for k in klines]  # 成交量
    
    def analyze_symbol(self, symbol):
        """专业技术分析"""
        data = self.price_data[symbol]
        prices = data["prices"]
        highs = data["highs"]
        lows = data["lows"]
        volumes = data["volumes"]
        
        # 降低数据要求，20根K线即可分析
        if len(prices) < 20:
            return None
        
        ta = TechnicalAnalysis()
        
        # 计算指标
        current_price = prices[-1]
        sma_20 = ta.calculate_sma(prices, 20)
        sma_50 = ta.calculate_sma(prices, 50)
        rsi = ta.calculate_rsi(prices, 14)
        atr = ta.calculate_atr(highs, lows, prices, 14)
        adx = ta.calculate_adx(highs, lows, prices, 14)
        bb_upper, bb_middle, bb_lower = ta.calculate_bollinger_bands(prices, 20, 2)
        
        # 成交量分析
        vol_sma = ta.calculate_sma(volumes, 20) if len(volumes) >= 20 else sum(volumes) / len(volumes)
        current_vol = volumes[-1]
        volume_spike = current_vol > vol_sma * 1.5 if vol_sma else False
        
        # 趋势判断 (多维度)
        trend = "NEUTRAL"
        trend_strength = 0
        
        # 均线判断
        if current_price > sma_20 > sma_50:
            trend = "LONG"
            trend_strength += 1
        elif current_price < sma_20 < sma_50:
            trend = "SHORT"
            trend_strength += 1
        
        # ADX趋势强度过滤
        if adx > CONFIG["adx_threshold"]:
            trend_strength += 1
        
        # RSI过滤 (避免超买超卖)
        rsi_signal = "NEUTRAL"
        if rsi < CONFIG["rsi_oversold"]:
            rsi_signal = "LONG"
        elif rsi > CONFIG["rsi_overbought"]:
            rsi_signal = "SHORT"
        
        # 布林带位置
        bb_position = "MIDDLE"
        if bb_upper and bb_lower:
            if current_price > bb_upper:
                bb_position = "ABOVE_UPPER"
            elif current_price < bb_lower:
                bb_position = "BELOW_LOWER"
        
        return {
            "symbol": symbol,
            "price": current_price,
            "sma_20": sma_20,
            "sma_50": sma_50,
            "rsi": rsi,
            "rsi_signal": rsi_signal,
            "atr": atr,
            "adx": adx,
            "trend": trend,
            "trend_strength": trend_strength,
            "volume_spike": volume_spike,
            "bb_position": bb_position,
            "atr_pct": (atr / current_price * 100) if current_price > 0 else 0
        }
    
    def generate_signal(self, analysis):
        """生成交易信号 - 激进进攻模式"""
        if not analysis:
            return None
        
        # 基本过滤 - ADX有趋势即可
        if analysis["adx"] < CONFIG["adx_threshold"]:
            return None
        
        # 成交量过滤 - 可配置是否强制
        volume_ok = analysis["volume_spike"] or not CONFIG.get("require_volume_spike", True)
        
        signal = None
        confidence = 0
        
        # 激进做多条件 - 满足2个即可
        long_scores = [
            analysis["trend"] == "LONG",  # +1
            analysis["rsi_signal"] in ["LONG", "NEUTRAL"],  # +1
            analysis["bb_position"] in ["MIDDLE", "BELOW_LOWER"],  # +1
            volume_ok,  # +1
            analysis["price"] > analysis["sma_20"]  # 价格在MA20之上 +1
        ]
        long_score = sum(long_scores)
        
        if long_score >= 2:  # 只需2分即可做多
            signal = "LONG"
            confidence = long_score
        
        # 激进做空条件
        short_scores = [
            analysis["trend"] == "SHORT",
            analysis["rsi_signal"] in ["SHORT", "NEUTRAL"],
            analysis["bb_position"] in ["MIDDLE", "ABOVE_UPPER"],
            volume_ok,
            analysis["price"] < analysis["sma_20"]
        ]
        short_score = sum(short_scores)
        
        if short_score >= 2:
            signal = "SHORT"
            confidence = short_score
        
        # 生成信号
        if signal and confidence >= 1:  # 最低1分即可交易
            price = analysis["price"]
            atr = analysis["atr"]
            atr_pct = atr / price if price > 0 else 0.01
            
            # 固定止损止盈 (更激进的固定比例)
            stop_loss_pct = max(CONFIG["stop_loss_pct"], atr_pct * 1.5)
            take_profit_pct = CONFIG["take_profit_pct"]
            
            if signal == "LONG":
                stop_loss = price * (1 - stop_loss_pct)
                take_profit = price * (1 + take_profit_pct)
            else:
                stop_loss = price * (1 + stop_loss_pct)
                take_profit = price * (1 - take_profit_pct)
            
            risk = price - stop_loss if signal == "LONG" else stop_loss - price
            reward = take_profit - price if signal == "LONG" else price - take_profit
            risk_reward = abs(reward / risk) if risk != 0 else 0
            
            # 2:1盈亏比即可
            if risk_reward >= CONFIG["min_risk_reward"]:
                log(f"📊 信号生成: {analysis['symbol']} {signal} | "
                    f"置信度:{confidence}/5 | ADX:{analysis['adx']:.1f} | "
                    f"盈亏比:{risk_reward:.1f}:1")
                
                return {
                    "signal": signal,
                    "symbol": analysis["symbol"],
                    "price": price,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "risk_reward": risk_reward,
                    "confidence": confidence,
                    "atr": atr,
                    "stop_loss_pct": stop_loss_pct
                }
        
        return None
    
    def calculate_position_size(self, stop_loss_pct, current_price):
        """凯利公式仓位计算
        
        Args:
            stop_loss_pct: 止损比例 (如 0.015 表示 1.5%)
            current_price: 当前价格
        
        Returns:
            交易数量 (以基础货币为单位，如BTC)
        """
        account = make_request("/fapi/v2/account")
        if 'availableBalance' not in account:
            log(f"⚠️ 无法获取账户余额", "WARN")
            return 0
        
        balance = float(account['availableBalance'])
        
        if balance <= 0:
            log(f"⚠️ 可用余额为0", "WARN")
            return 0
        
        if current_price <= 0:
            log(f"⚠️ 当前价格无效", "WARN")
            return 0
        
        # 风险金额 (本金的10%)
        risk_usdt = balance * CONFIG["risk_per_trade"]
        
        # 基于止损距离计算名义仓位价值
        if stop_loss_pct <= 0:
            log(f"⚠️ 止损比例为0", "WARN")
            return 0
        
        # 目标名义仓位价值 (USDT)
        target_notional = risk_usdt / stop_loss_pct
        
        # 应用杠杆限制 (最多使用50%可用保证金)
        max_notional = balance * CONFIG["leverage"] * 0.5
        notional_value = min(target_notional, max_notional)
        
        # 计算实际交易数量 (BTC数量 = 名义价值 / 当前价格)
        quantity = notional_value / current_price
        
        # BTC合约最小数量是0.001
        if quantity < 0.001:
            log(f"⚠️ 计算数量 {quantity:.6f} BTC 小于最小交易单位 0.001", "WARN")
            return 0
        
        # 最大不超过5 BTC (安全限制)
        quantity = min(quantity, 5.0)
        
        required_margin = notional_value / CONFIG["leverage"]
        log(f"📊 仓位计算: 余额={balance:.2f}USDT, 风险={risk_usdt:.2f}USDT, 止损={stop_loss_pct*100:.2f}%, "
            f"名义价值={notional_value:.2f}USDT, 数量={quantity:.4f}BTC, 需保证金={required_margin:.2f}USDT")
        
        return round(quantity, 4)
    
    def get_position(self, symbol):
        """获取持仓"""
        result = make_request("/fapi/v2/positionRisk", {"symbol": symbol})
        if isinstance(result, list):
            for pos in result:
                if pos['symbol'] == symbol and float(pos['positionAmt']) != 0:
                    return pos
        return None
    
    def open_position(self, signal):
        """开仓"""
        symbol = signal["symbol"]
        side = "BUY" if signal["signal"] == "LONG" else "SELL"
        current_price = signal["price"]
        
        stop_loss_pct = signal.get("stop_loss_pct", abs(current_price - signal["stop_loss"]) / current_price)
        quantity = self.calculate_position_size(stop_loss_pct, current_price)
        
        if quantity <= 0:
            log(f"⚠️ 仓位计算为0，跳过", "WARN")
            return False
        
        log(f"🟢 [{signal['confidence']}/3] 开仓 {side} {symbol} @ ${signal['price']:.2f}")
        log(f"   数量: {quantity}, 止损: ${signal['stop_loss']:.2f}, 止盈: ${signal['take_profit']:.2f}")
        log(f"   盈亏比: {signal['risk_reward']:.1f}:1, ATR: ${signal['atr']:.2f}")
        
        result = make_post_request("/fapi/v1/order", {
            "symbol": symbol,
            "side": side,
            "type": "MARKET",
            "quantity": quantity
        })
        
        if 'orderId' in result:
            log(f"✅ 开仓成功: OrderID={result['orderId']}, 成交价=${result.get('avgPrice', 'N/A')}")
            self.positions[symbol] = {
                "entry": float(result.get('avgPrice', signal['price'])),
                "side": signal["signal"],
                "quantity": quantity,
                "stop_loss": signal["stop_loss"],
                "take_profit": signal["take_profit"],
                "opened_at": time.time()
            }
            self.total_trades += 1
            return True
        else:
            log(f"❌ 开仓失败: {result.get('msg', result.get('error'))}", "ERROR")
            return False
    
    def close_position(self, symbol, reason=""):
        """平仓"""
        pos = self.get_position(symbol)
        if not pos:
            return False
        
        amt = float(pos['positionAmt'])
        side = "SELL" if amt > 0 else "BUY"
        qty = abs(amt)
        
        log(f"🔴 平仓 {side} {symbol} | 原因: {reason}")
        
        result = make_post_request("/fapi/v1/order", {
            "symbol": symbol,
            "side": side,
            "type": "MARKET",
            "quantity": qty
        })
        
        if 'orderId' in result:
            pnl = float(pos.get('unRealizedProfit', 0))
            log(f"✅ 平仓成功: PnL=${pnl:+.2f}")
            
            # 更新统计
            if pnl > 0:
                self.daily_stats["wins"] += 1
                self.consecutive_losses = 0
                self.cooldown_until = time.time() + CONFIG["cooldown_after_win"]
            else:
                self.daily_stats["losses"] += 1
                self.consecutive_losses += 1
                self.cooldown_until = time.time() + CONFIG["cooldown_after_loss"]
            
            self.daily_stats["pnl"] += pnl
            
            if symbol in self.positions:
                del self.positions[symbol]
            return True
        else:
            log(f"❌ 平仓失败: {result.get('msg', result.get('error'))}", "ERROR")
            return False
    
    def manage_positions(self):
        """持仓管理 (激进止盈止损)"""
        for symbol, pos_info in list(self.positions.items()):
            pos = self.get_position(symbol)
            if not pos:
                continue
            
            current_price = float(pos['markPrice'])
            entry = float(pos['entryPrice'])
            amt = float(pos['positionAmt'])
            side = "LONG" if amt > 0 else "SHORT"
            pnl_pct = (current_price - entry) / entry * 100
            
            if side == "SHORT":
                pnl_pct = -pnl_pct
            
            # 获取持仓信息
            pos_data = self.positions.get(symbol, {})
            highest_pnl = pos_data.get("highest_pnl", 0)
            
            # 更新最高盈利
            if pnl_pct > highest_pnl:
                self.positions[symbol]["highest_pnl"] = pnl_pct
                highest_pnl = pnl_pct
            
            # 固定止损 -2%
            if pnl_pct <= -CONFIG["stop_loss_pct"] * 100:
                self.close_position(symbol, f"止损 {pnl_pct:.2f}%")
                continue
            
            # 固定止盈 +4%
            if pnl_pct >= CONFIG["take_profit_pct"] * 100:
                self.close_position(symbol, f"止盈 {pnl_pct:.2f}%")
                continue
            
            # 追踪止盈 - 盈利回撤1.5%平仓
            if CONFIG.get("use_trailing", False) and highest_pnl > 2:
                drawdown = highest_pnl - pnl_pct
                if drawdown >= CONFIG.get("trailing_stop", 0.015) * 100:
                    self.close_position(symbol, f"追踪止盈 最高:{highest_pnl:.2f}% 当前:{pnl_pct:.2f}% 回撤:{drawdown:.2f}%")
                    continue
            
            # 盈亏平衡保护 - 盈利超过2%后，止损移到成本价
            if highest_pnl > 2 and pnl_pct <= 0.3:
                self.close_position(symbol, f"保本出场 {pnl_pct:.2f}%")
                continue
            elif pnl_pct <= -2:
                self.close_position(symbol, "止损2%")
    
    def check_risk_limits(self):
        """检查风险限制"""
        account = make_request("/fapi/v2/account")
        if 'totalWalletBalance' not in account:
            return True
        
        balance = float(account['totalWalletBalance'])
        daily_loss = CONFIG["initial_balance"] - balance
        
        # 日止损
        if daily_loss >= CONFIG["max_daily_loss"]:
            log(f"🛑 日止损触发: 亏损 ${daily_loss:.2f}，暂停交易", "WARN")
            return False
        
        # 连续亏损限制
        if self.consecutive_losses >= 3:
            log(f"🛑 连续{self.consecutive_losses}次亏损，暂停30分钟", "WARN")
            self.cooldown_until = time.time() + 1800
            self.consecutive_losses = 0
        
        return True
    
    def run(self):
        """主循环"""
        log("="*60)
        log("🔥🔥🔥 激进进攻模式启动 🔥🔥🔥")
        log("="*60)
        log(f"💰 目标: 3天盈利 {CONFIG['target_profit']*100}% (不赚钱就是亏!)")
        log(f"⚡ 频率: 每{CONFIG['check_interval']}秒监控")
        log(f"📊 币种: {', '.join(CONFIG['symbols'])}")
        log(f"🎯 杠杆: {CONFIG['leverage']}x | 单笔风险: {CONFIG['risk_per_trade']*100}%")
        log(f"🛡️ 止损: {CONFIG['stop_loss_pct']*100}% | 止盈: {CONFIG['take_profit_pct']*100}%")
        log(f"📈 门槛: 置信度>=1即可交易 | 盈亏比>={CONFIG['min_risk_reward']}:1")
        log("="*60)
        log("⚠️ 警告: 激进策略，高风险高收益！")
        log("="*60)
        
        while True:
            try:
                # 冷却检查
                if time.time() < self.cooldown_until:
                    remaining = int(self.cooldown_until - time.time())
                    if remaining % 60 == 0:  # 每分钟报一次
                        log(f"⏳ 冷却中...剩余{remaining}秒")
                    time.sleep(1)
                    continue
                
                # 更新市场数据
                self.update_market_data()
                
                # 管理现有持仓
                self.manage_positions()
                
                # 风险检查
                if not self.check_risk_limits():
                    time.sleep(3600)
                    continue
                
                # 检查持仓数量
                active_positions = len([p for p in self.positions.values() if p])
                if active_positions >= CONFIG["max_positions"]:
                    time.sleep(CONFIG["check_interval"])
                    continue
                
                # 寻找机会
                best_signal = None
                best_confidence = 0
                
                for symbol in CONFIG["symbols"]:
                    analysis = self.analyze_symbol(symbol)
                    if analysis:
                        signal = self.generate_signal(analysis)
                        if signal and signal["confidence"] > best_confidence:
                            best_signal = signal
                            best_confidence = signal["confidence"]
                
                # 执行最佳信号 - 激进模式：置信度>=1即可交易
                if best_signal and best_confidence >= 1:
                    log(f"🎯【进攻】信号: {best_signal['symbol']} {best_signal['signal']} | 置信度:{best_confidence}/5 | 盈亏比:{best_signal['risk_reward']:.1f}:1")
                    self.open_position(best_signal)
                elif best_signal:
                    log(f"📊 信号不足: {best_signal['symbol']} 置信度{best_confidence}/5 (需要>=1)")
                
                # 状态显示
                account = make_request("/fapi/v2/account")
                if 'totalWalletBalance' in account:
                    balance = float(account['totalWalletBalance'])
                    pnl = balance - CONFIG["initial_balance"]
                    pnl_pct = (pnl / CONFIG["initial_balance"]) * 100
                    
                    positions_info = ", ".join([f"{s}: {p['side']}" for s, p in self.positions.items()]) or "无"
                    log(f"💰 余额: ${balance:.2f} ({pnl:+.2f}, {pnl_pct:+.1f}%) | 持仓: {positions_info}")
                
                time.sleep(CONFIG["check_interval"])
                
            except KeyboardInterrupt:
                log("🛑 用户中断，停止交易")
                break
            except Exception as e:
                log(f"❌ 错误: {e}", "ERROR")
                time.sleep(10)

# ========== 启动 ==========
if __name__ == "__main__":
    bot = ProTradingBot()
    bot.run()
