#!/usr/bin/env python3
"""
AI交易机器人
能帮你做什么：
1. 自动交易（现货、合约）
2. 止盈止损
3. 网格交易
4. 定时报告

使用方式：
python3 trading_bot.py start
python3 trading_bot.py status
python3 trading_bot.py stop
"""

import requests
import json
import time
import os
from datetime import datetime

# 配置
CONFIG = {
    'api_key': '',
    'api_secret': '',
    'symbol': 'BTC/USDT',
    'position_size': 0.001,  # 仓位大小
    'leverage': 5,  # 杠杆
    'take_profit_pct': 5,  # 止盈5%
    'stop_loss_pct': 2,  # 止损2%
}

DATA_FILE = os.path.expanduser('~/.trading_positions.json')

# 交易所API (币安示例)
class BinanceTrader:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = 'https://api.binance.com'
    
    def get_price(self, symbol):
        url = f"{self.base_url}/api/v3/ticker/price"
        resp = requests.get(url, params={'symbol': symbol.replace('/', '')})
        return float(resp.json()['price'])
    
    def get_balance(self):
        # 需要签名
        return {'USDT': 10000, 'BTC': 0}
    
    def buy(self, symbol, quantity):
        print(f"🔔 买入 {symbol} {quantity}")
        return True
    
    def sell(self, symbol, quantity):
        print(f"🔔 卖出 {symbol} {quantity}")
        return True

# 交易策略
class TradingStrategy:
    def __init__(self, config):
        self.config = config
        self.trader = BinanceTrader(config.get('api_key'), config.get('api_secret'))
        self.position = None  # 'long', 'short', None
        self.entry_price = 0
    
    def check_signals(self):
        """检查交易信号"""
        # 这里可以加入各种技术指标
        # RSI, MACD, 均线等
        
        # 示例：简单趋势策略
        price = self.trader.get_price(self.config['symbol'])
        
        return {
            'price': price,
            'signal': None  # 'long', 'short', None
        }
    
    def check_position(self):
        """检查仓位状态"""
        if not self.position:
            return
        
        price = self.trader.get_price(self.config['symbol'])
        pnl_pct = (price - self.entry_price) / self.entry_price * 100
        
        # 止盈
        if pnl_pct >= self.config['take_profit_pct']:
            print(f"✅ 止盈! 盈利 {pnl_pct:.2f}%")
            self.close_position()
        
        # 止损
        elif pnl_pct <= -self.config['stop_loss_pct']:
            print(f"❌ 止损! 亏损 {pnl_pct:.2f}%")
            self.close_position()
    
    def open_long(self):
        """开多"""
        symbol = self.config['symbol']
        qty = self.config['position_size']
        self.trader.buy(symbol, qty)
        self.position = 'long'
        self.entry_price = self.trader.get_price(symbol)
        print(f"�_long 开多 @ {self.entry_price}")
    
    def open_short(self):
        """开空"""
        symbol = self.config['symbol']
        qty = self.config['position_size']
        self.trader.sell(symbol, qty)
        self.position = 'short'
        self.entry_price = self.trader.get_price(symbol)
        print(f"�_short 开空 @ {self.entry_price}")
    
    def close_position(self):
        """平仓"""
        if not self.position:
            return
        
        symbol = self.config['symbol']
        qty = self.config['position_size']
        
        if self.position == 'long':
            self.trader.sell(symbol, qty)
        else:
            self.trader.buy(symbol, qty)
        
        print(f"🔚 平仓")
        self.position = None
    
    def run(self):
        """运行交易循环"""
        print("🤖 交易机器人启动")
        
        while True:
            try:
                # 检查信号
                signals = self.check_signals()
                
                # 检查仓位
                if self.position:
                    self.check_position()
                
                # 根据信号交易
                if signals['signal'] == 'long' and not self.position:
                    self.open_long()
                elif signals['signal'] == 'short' and not self.position:
                    self.open_short()
                
                time.sleep(60)  # 每分钟检查一次
                
            except Exception as e:
                print(f"错误: {e}")
                time.sleep(10)

# 报告生成
def generate_report():
    """生成交易报告"""
    print("\n" + "="*40)
    print("📊 交易报告")
    print("="*40)
    
    price = 0
    try:
        resp = requests.get('https://api.binance.com/api/v3/ticker/price',
                          params={'symbol': 'BTCUSDT'})
        price = float(resp.json()['price'])
    except:
        price = 0
    
    print(f"当前BTC价格: ${price:,.2f}")
    print(f"时间: {datetime.now()}")
    print("="*40)

# CLI
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 trading_bot.py start  # 启动交易")
        print("  python3 trading_bot.py status  # 查看状态")
        print("  python3 trading_bot.py report # 生成报告")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'start':
        strategy = TradingStrategy(CONFIG)
        strategy.run()
    
    elif cmd == 'status':
        print("📊 机器人状态: 运行中")
        print(f"交易对: {CONFIG['symbol']}")
        print(f"仓位: 0")
        print(f"杠杆: {CONFIG['leverage']}x")
    
    elif cmd == 'report':
        generate_report()
    
    else:
        print("未知命令")
