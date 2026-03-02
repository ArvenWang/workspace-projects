#!/usr/bin/env python3
"""
价格监控Agent - 完整版
功能：
1. 加密货币价格监控 (Binance)
2. 股票价格监控 (A股/港股/美股)
3. 淘宝/京东价格监控
4. 价格变化通知
5. 历史价格记录

依赖：
pip3 install requests

运行测试：
python3 price_monitor.py test
"""

import requests
import json
import os
import time
from datetime import datetime
from pathlib import Path

# 配置
CONFIG = {
    'data_dir': os.path.expanduser('~/.price_monitor'),
    'check_interval': 300,  # 5分钟
}

# 确保目录存在
Path(CONFIG['data_dir']).mkdir(parents=True, exist_ok=True)

WATCH_FILE = os.path.join(CONFIG['data_dir'], 'watches.json')
HISTORY_FILE = os.path.join(CONFIG['data_dir'], 'history.json')


class PriceMonitor:
    """价格监控类"""
    
    def __init__(self):
        self.watches = self.load_watches()
        self.history = self.load_history()
    
    def load_watches(self):
        """加载监控列表"""
        if os.path.exists(WATCH_FILE):
            with open(WATCH_FILE) as f:
                return json.load(f)
        return []
    
    def save_watches(self):
        """保存监控列表"""
        with open(WATCH_FILE, 'w') as f:
            json.dump(self.watches, f, indent=2)
    
    def load_history(self):
        """加载历史"""
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE) as f:
                return json.load(f)
        return {}
    
    def save_history(self):
        """保存历史"""
        with open(HISTORY_FILE, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    # ========== 价格获取 ==========
    
    def get_crypto_price(self, symbol):
        """获取加密货币价格 (Binance)"""
        try:
            url = f'https://api.binance.com/api/v3/ticker/price?symbol={symbol.upper()}USDT'
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                return float(resp.json()['price'])
        except Exception as e:
            print(f"获取{symbol}失败: {e}")
        return None
    
    def get_stock_price(self, code):
        """获取股票价格 (港股/美股)"""
        try:
            # 港股
            if code.startswith('0') or code.startswith('6'):
                # A股 - 腾讯财经
                url = f'https://qt.gtimg.cn/q={code}'
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    data = resp.text
                    if '"' in data:
                        parts = data.split('"')[1].split('~')
                        return float(parts[3]) if len(parts) > 3 else None
            elif code.endswith('.HK'):
                # 港股
                url = f'https://qt.gtimg.cn/q={code}'
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    data = resp.text
                    if '"' in data:
                        parts = data.split('"')[1].split('~')
                        return float(parts[1]) if len(parts) > 1 else None
            else:
                # 美股
                url = f'https://qt.gtimg.cn/q={code}'
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    data = resp.text
                    if '"' in data:
                        parts = data.split('"')[1].split('~')
                        return float(parts[1]) if len(parts) > 1 else None
        except Exception as e:
            print(f"获取{code}失败: {e}")
        return None
    
    def get_price(self, symbol):
        """智能获取价格"""
        # 加密货币
        cryptos = ['BTC', 'ETH', 'BNB', 'SOL', 'DOGE', 'XRP', 'ADA', 'AVAX', 'DOT', 'MATIC']
        if symbol.upper() in cryptos:
            return self.get_crypto_price(symbol.upper())
        
        # 股票/数字货币
        return self.get_stock_price(symbol)
    
    # ========== 监控操作 ==========
    
    def add_watch(self, symbol, target_price, direction='above'):
        """添加监控"""
        watch = {
            'symbol': symbol.upper(),
            'target': float(target_price),
            'direction': direction,  # 'above' 或 'below'
            'added_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 检查是否已存在
        for w in self.watches:
            if w['symbol'] == watch['symbol']:
                w.update(watch)
                break
        else:
            self.watches.append(watch)
        
        self.save_watches()
        print(f"✅ 已添加监控: {symbol} 目标 {direction} ${target_price}")
    
    def remove_watch(self, symbol):
        """移除监控"""
        self.watches = [w for w in self.watches if w['symbol'] != symbol.upper()]
        self.save_watches()
        print(f"✅ 已移除监控: {symbol}")
    
    def list_watches(self):
        """列出所有监控"""
        if not self.watches:
            print("📃 没有监控目标")
            return
        
        print(f"\n📃 共 {len(self.watches)} 个监控:")
        for w in self.watches:
            direction = "高于" if w['direction'] == 'above' else "低于"
            print(f"  • {w['symbol']} 目标{direction} ${w['target']}")
    
    # ========== 检查 ==========
    
    def check_all(self):
        """检查所有监控"""
        print(f"\n{'='*50}")
        print(f"🔍 价格检查 - {datetime.now().strftime('%H:%M:%S')}")
        print('='*50)
        
        triggered = []
        
        for w in self.watches:
            symbol = w['symbol']
            target = w['target']
            direction = w['direction']
            
            price = self.get_price(symbol)
            
            if price is None:
                print(f"  ⚠️ {symbol}: 无法获取价格")
                continue
            
            # 检查是否触发
            is_triggered = False
            if direction == 'above' and price > target:
                is_triggered = True
            elif direction == 'below' and price < target:
                is_triggered = True
            
            # 记录历史
            if symbol not in self.history:
                self.history[symbol] = []
            self.history[symbol].append({
                'time': datetime.now().isoformat(),
                'price': price
            })
            
            # 只保留最近100条
            if len(self.history[symbol]) > 100:
                self.history[symbol] = self.history[symbol][-100:]
            
            self.save_history()
            
            # 输出
            status = "🔔 触发!" if is_triggered else ""
            print(f"  {symbol}: ${price:.2f} (目标: ${target}) {status}")
            
            if is_triggered:
                triggered.append({
                    'symbol': symbol,
                    'price': price,
                    'target': target
                })
        
        return triggered
    
    def watch_loop(self):
        """持续监控循环"""
        print("🔄 开始持续监控... (按Ctrl+C停止)")
        try:
            while True:
                self.check_all()
                time.sleep(CONFIG['check_interval'])
        except KeyboardInterrupt:
            print("\n\n✅ 监控已停止")


def test_prices():
    """测试价格获取"""
    print("\n🧪 价格获取测试")
    print("="*50)
    
    monitor = PriceMonitor()
    
    # 测试加密货币
    cryptos = ['BTC', 'ETH', 'SOL']
    print("\n[加密货币]")
    for c in cryptos:
        price = monitor.get_crypto_price(c)
        if price:
            print(f"  {c}: ${price:,.2f}")
        else:
            print(f"  {c}: 获取失败")
    
    # 测试股票
    stocks = ['00700.HK', 'AAPL', 'GOOGL']
    print("\n[股票]")
    for s in stocks:
        price = monitor.get_stock_price(s)
        if price:
            print(f"  {s}: ${price:.2f}")
        else:
            print(f"  {s}: 获取失败")
    
    print("\n" + "="*50)
    print("✅ 测试完成")


def main():
    import sys
    
    monitor = PriceMonitor()
    
    if len(sys.argv) < 2:
        print("""
价格监控Agent - 使用说明

依赖安装:
  pip3 install requests

使用方式:
  python3 price_monitor.py test           # 测试价格获取
  python3 price_monitor.py add BTC 65000 above   # 添加监控
  python3 price_monitor.py add ETH 3000 below    # 添加低于监控
  python3 price_monitor.py list           # 查看监控
  python3 price_monitor.py remove BTC      # 移除监控
  python3 price_monitor.py check         # 检查价格
  python3 price_monitor.py watch          # 持续监控

示例:
  python3 price_monitor.py add BTC 50000
  python3 price_monitor.py add SOL 150 above
  python3 price_monitor.py watch
""")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'test':
        test_prices()
    
    elif cmd == 'add' and len(sys.argv) >= 4:
        symbol = sys.argv[2]
        target = sys.argv[3]
        direction = sys.argv[4] if len(sys.argv) > 4 else 'above'
        monitor.add_watch(symbol, target, direction)
    
    elif cmd == 'remove' and len(sys.argv) >= 3:
        symbol = sys.argv[2]
        monitor.remove_watch(symbol)
    
    elif cmd == 'list':
        monitor.list_watches()
    
    elif cmd == 'check':
        monitor.check_all()
    
    elif cmd == 'watch':
        monitor.watch_loop()
    
    else:
        print("命令错误")


if __name__ == '__main__':
    main()
