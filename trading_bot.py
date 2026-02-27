#!/usr/bin/env python3
"""
高频交易监控机器人 - 3天50%盈利目标
运行时间: 2026-02-23 至 2026-02-26
"""

import time
import json
import base64
import csv
import os
import sys
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import urllib.request

# ========== 配置 ==========
CONFIG = {
    "api_key": "Rzb1qhBd3BkIGLCO4rH7pTjPt1KZpq7lbgfIp0np81gOdq6xF9p7oFzqXq0cpLvs",
    "private_key_b64": "MC4CAQAwBQYDK2VwBCIEIISJgEmcDMko/bVi5n3nkDxNHpztDrqB08Ug5gGLDjdF",
    "symbol": "BTCUSDT",
    "check_interval": 30,  # 每30秒检查一次
    "target_profit": 0.50,  # 50%目标
    "initial_balance": 50,  # 初始50 USDT
    "max_daily_loss": 15,   # 日最大亏损15 USDT
    "leverage": 5,          # 5倍杠杆
    "data_dir": os.path.expanduser("~/.openclaw/workspace/trading_data"),
}

# ========== 初始化密钥 ==========
full_key = base64.b64decode(CONFIG["private_key_b64"])
seed = full_key[16:48]
PRIVATE_KEY = Ed25519PrivateKey.from_private_bytes(seed)

# ========== 工具函数 ==========
def log(msg, level="INFO"):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {msg}"
    print(log_line)
    
    log_file = os.path.join(CONFIG["data_dir"], f"trades_{datetime.now().strftime('%Y%m%d')}.log")
    with open(log_file, "a") as f:
        f.write(log_line + "\n")

def make_request(endpoint, params=None, base_url="https://fapi.binance.com"):
    """发送带签名的API请求"""
    try:
        # 获取服务器时间
        with urllib.request.urlopen("https://api.binance.com/api/v3/time", timeout=10) as resp:
            server_time = json.loads(resp.read().decode())['serverTime']
    except:
        server_time = int(time.time() * 1000)
    
    if params is None:
        params = {}
    params['timestamp'] = server_time
    
    payload = '&'.join([f"{k}={v}" for k, v in params.items()])
    signature = PRIVATE_KEY.sign(payload.encode('utf-8'))
    sig_b64 = base64.b64encode(signature).decode('utf-8')
    
    url = f"{base_url}{endpoint}?{payload}&signature={sig_b64}"
    req = urllib.request.Request(url, headers={'X-MBX-APIKEY': CONFIG["api_key"]})
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        err = json.loads(e.read().decode())
        return {"code": err.get('code'), "msg": err.get('msg')}
    except Exception as e:
        return {"error": str(e)}

def make_post_request(endpoint, params, base_url="https://fapi.binance.com"):
    """发送POST请求"""
    try:
        with urllib.request.urlopen("https://api.binance.com/api/v3/time", timeout=10) as resp:
            server_time = json.loads(resp.read().decode())['serverTime']
    except:
        server_time = int(time.time() * 1000)
    
    params['timestamp'] = server_time
    payload = '&'.join([f"{k}={v}" for k, v in params.items()])
    
    signature = PRIVATE_KEY.sign(payload.encode('utf-8'))
    sig_b64 = base64.b64encode(signature).decode('utf-8')
    
    url = f"{base_url}{endpoint}"
    data = f"{payload}&signature={sig_b64}"
    
    req = urllib.request.Request(url, data=data.encode('utf-8'), headers={
        'X-MBX-APIKEY': CONFIG["api_key"],
        'Content-Type': 'application/x-www-form-urlencoded'
    }, method='POST')
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        err = json.loads(e.read().decode())
        return {"code": err.get('code'), "msg": err.get('msg')}
    except Exception as e:
        return {"error": str(e)}

# ========== 交易逻辑 ==========
class TradingBot:
    def __init__(self):
        self.price_history = []
        self.position = None
        self.daily_pnl = 0
        self.total_pnl = 0
        self.trades_today = 0
        self.last_report_hour = -1
        
    def get_price(self):
        """获取当前价格"""
        result = make_request("/fapi/v1/ticker/price", {"symbol": CONFIG["symbol"]})
        if 'price' in result:
            return float(result['price'])
        return None
    
    def get_account(self):
        """获取账户信息"""
        return make_request("/fapi/v2/account")
    
    def get_position(self):
        """获取当前持仓"""
        result = make_request("/fapi/v2/positionRisk", {"symbol": CONFIG["symbol"]})
        if isinstance(result, list):
            for pos in result:
                if pos['symbol'] == CONFIG["symbol"] and float(pos['positionAmt']) != 0:
                    return pos
        return None
    
    def analyze_trend(self):
        """分析趋势"""
        if len(self.price_history) < 20:
            return "NEUTRAL"
        
        # 简单趋势判断
        recent = self.price_history[-10:]
        older = self.price_history[-20:-10]
        
        avg_recent = sum(recent) / len(recent)
        avg_older = sum(older) / len(older)
        
        change_pct = (avg_recent - avg_older) / avg_older * 100
        
        if change_pct > 0.5:
            return "LONG"
        elif change_pct < -0.5:
            return "SHORT"
        return "NEUTRAL"
    
    def calculate_position_size(self):
        """计算仓位大小"""
        account = self.get_account()
        if 'availableBalance' in account:
            balance = float(account['availableBalance'])
            # 使用10-20%可用资金
            return round(balance * 0.15 / CONFIG["leverage"], 4)
        return 0.001  # 默认最小仓位
    
    def open_position(self, side, quantity):
        """开仓"""
        log(f"🟢 开仓 {side} {quantity} {CONFIG['symbol']}")
        result = make_post_request("/fapi/v1/order", {
            "symbol": CONFIG["symbol"],
            "side": side,
            "type": "MARKET",
            "quantity": quantity,
            "leverage": CONFIG["leverage"]
        })
        
        if 'orderId' in result:
            log(f"✅ 开仓成功: OrderID={result['orderId']}")
            return True
        else:
            log(f"❌ 开仓失败: {result.get('msg', result.get('error'))}", "ERROR")
            return False
    
    def close_position(self, side, quantity):
        """平仓"""
        log(f"🔴 平仓 {side} {quantity} {CONFIG['symbol']}")
        result = make_post_request("/fapi/v1/order", {
            "symbol": CONFIG["symbol"],
            "side": side,
            "type": "MARKET",
            "quantity": quantity
        })
        
        if 'orderId' in result:
            log(f"✅ 平仓成功: OrderID={result['orderId']}")
            return True
        else:
            log(f"❌ 平仓失败: {result.get('msg', result.get('error'))}", "ERROR")
            return False
    
    def set_leverage(self, leverage):
        """设置杠杆"""
        result = make_post_request("/fapi/v1/leverage", {
            "symbol": CONFIG["symbol"],
            "leverage": leverage
        })
        if 'leverage' in result:
            log(f"✅ 杠杆设置: {result['leverage']}x")
            return True
        return False
    
    def record_price(self, price):
        """记录价格"""
        self.price_history.append(price)
        if len(self.price_history) > 100:
            self.price_history = self.price_history[-100:]
        
        # 写入CSV
        csv_file = os.path.join(CONFIG["data_dir"], f"prices_{CONFIG['symbol']}.csv")
        with open(csv_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                price,
                self.position['side'] if self.position else "NONE",
                self.position['amt'] if self.position else 0,
                self.total_pnl
            ])
    
    def check_and_report(self):
        """检查并汇报"""
        current_hour = datetime.now().hour
        
        # 每2小时简报
        if current_hour % 2 == 0 and current_hour != self.last_report_hour:
            self.last_report_hour = current_hour
            self.send_brief_report()
        
        # 每晚22:00详细汇报
        if current_hour == 22 and datetime.now().minute < 5:
            self.send_detailed_report()
    
    def send_brief_report(self):
        """发送简报"""
        account = self.get_account()
        position = self.get_position()
        price = self.get_price()
        
        if 'totalWalletBalance' in account:
            balance = float(account['totalWalletBalance'])
            profit_pct = (balance - CONFIG["initial_balance"]) / CONFIG["initial_balance"] * 100
            
            msg = f"📊 交易简报 {datetime.now().strftime('%H:%M')}\n"
            msg += f"余额: {balance:.2f} USDT ({profit_pct:+.2f}%)\n"
            msg += f"持仓: {position['positionAmt'] if position else '无'}\n"
            msg += f"BTC价格: ${price:.2f}" if price else ""
            
            log(msg)
    
    def send_detailed_report(self):
        """发送详细报告"""
        account = self.get_account()
        position = self.get_position()
        price = self.get_price()
        
        if 'totalWalletBalance' in account:
            balance = float(account['totalWalletBalance'])
            profit_pct = (balance - CONFIG["initial_balance"]) / CONFIG["initial_balance"] * 100
            
            msg = f"📈 每日交易报告 ({datetime.now().strftime('%Y-%m-%d')})\n"
            msg += "="*40 + "\n"
            msg += f"账户余额: {balance:.2f} USDT\n"
            msg += f"初始资金: {CONFIG['initial_balance']} USDT\n"
            msg += f"当前盈亏: {balance - CONFIG['initial_balance']:+.2f} USDT ({profit_pct:+.2f}%)\n"
            msg += f"目标进度: {profit_pct/CONFIG['target_profit']*100:.1f}%\n"
            msg += f"今日交易: {self.trades_today} 笔\n"
            
            if position:
                pnl = float(position.get('unRealizedProfit', 0))
                msg += f"当前持仓: {position['positionAmt']} BTC @ ${position['entryPrice']}\n"
                msg += f"未实现盈亏: {pnl:+.2f} USDT\n"
            
            msg += f"BTC价格: ${price:.2f}\n" if price else ""
            msg += "="*40
            
            log(msg)
            
            # 保存到JSON
            summary = {
                "date": datetime.now().strftime('%Y-%m-%d'),
                "balance": balance,
                "pnl": balance - CONFIG['initial_balance'],
                "pnl_pct": profit_pct,
                "trades": self.trades_today,
                "btc_price": price
            }
            
            json_file = os.path.join(CONFIG["data_dir"], "pnl_summary.json")
            try:
                with open(json_file, "r") as f:
                    data = json.load(f)
            except:
                data = []
            
            data.append(summary)
            with open(json_file, "w") as f:
                json.dump(data, f, indent=2)
    
    def run(self):
        """主循环"""
        log("="*50)
        log("🚀 高频交易机器人启动")
        log(f"目标: 3天盈利 {CONFIG['target_profit']*100}%")
        log(f"监控间隔: {CONFIG['check_interval']}秒")
        log(f"交易对: {CONFIG['symbol']}")
        log("="*50)
        
        # 设置杠杆
        self.set_leverage(CONFIG["leverage"])
        
        last_action = None
        action_cooldown = 0
        
        while True:
            try:
                # 获取当前价格
                price = self.get_price()
                if not price:
                    log("⚠️ 无法获取价格", "WARN")
                    time.sleep(5)
                    continue
                
                # 更新价格历史
                self.record_price(price)
                
                # 获取持仓
                position = self.get_position()
                
                # 分析趋势
                trend = self.analyze_trend()
                
                # 检查汇报
                self.check_and_report()
                
                # 交易逻辑
                if action_cooldown > 0:
                    action_cooldown -= 1
                else:
                    if position:
                        # 有持仓 - 检查止盈止损
                        entry_price = float(position['entryPrice'])
                        current_pnl_pct = (price - entry_price) / entry_price * 100
                        if position['positionSide'] == 'SHORT':
                            current_pnl_pct = -current_pnl_pct
                        
                        # 止盈 5% 或 止损 2%
                        if current_pnl_pct >= 5 or current_pnl_pct <= -2:
                            close_side = "SELL" if float(position['positionAmt']) > 0 else "BUY"
                            qty = abs(float(position['positionAmt']))
                            self.close_position(close_side, qty)
                            self.trades_today += 1
                            action_cooldown = 10  # 冷却5分钟
                    else:
                        # 无持仓 - 寻找机会
                        if trend == "LONG":
                            qty = self.calculate_position_size()
                            if self.open_position("BUY", qty):
                                self.trades_today += 1
                                action_cooldown = 10
                        elif trend == "SHORT":
                            qty = self.calculate_position_size()
                            if self.open_position("SELL", qty):
                                self.trades_today += 1
                                action_cooldown = 10
                
                # 显示状态
                if len(self.price_history) % 10 == 0:
                    log(f"💰 BTC: ${price:.2f} | 趋势: {trend} | 持仓: {position['positionAmt'] if position else '无'}")
                
                # 检查日止损
                account = self.get_account()
                if 'totalWalletBalance' in account:
                    balance = float(account['totalWalletBalance'])
                    daily_loss = CONFIG["initial_balance"] - balance
                    if daily_loss >= CONFIG["max_daily_loss"]:
                        log(f"⚠️ 日最大亏损达到 {daily_loss:.2f} USDT，暂停交易", "WARN")
                        time.sleep(3600)  # 暂停1小时
                
                time.sleep(CONFIG["check_interval"])
                
            except KeyboardInterrupt:
                log("🛑 用户中断，停止交易")
                break
            except Exception as e:
                log(f"❌ 错误: {e}", "ERROR")
                time.sleep(10)

# ========== 启动 ==========
if __name__ == "__main__":
    bot = TradingBot()
    bot.run()
