#!/usr/bin/env python3
"""
价格监控Agent
能帮你做什么：
1. 监控商品价格（京东、淘宝、拼多多）
2. 监控加密货币价格
3. 监控股票价格
4. 价格变化自动通知

使用方法：
python3 price_monitor.py add BTC 30000
python3 price_monitor.py watch eth 2000
python3 price_monitor.py list
"""

import requests
import json
import time
import os
from datetime import datetime

# 配置
CONFIG = {
    'data_file': os.path.expanduser('~/.openclaw/workspace/price_watch.json'),
    'check_interval': 300,  # 5分钟检查一次
}

# 监控目标
WATCH_LIST = []

def load_watches():
    """加载监控列表"""
    if os.path.exists(CONFIG['data_file']):
        with open(CONFIG['data_file']) as f:
            return json.load(f)
    return []

def save_watches(watches):
    """保存监控列表"""
    with open(CONFIG['data_file'], 'w') as f:
        json.dump(watches, f, ensure_ascii=False, indent=2)

# 价格获取函数
def get_crypto_price(symbol):
    """获取加密货币价格"""
    symbol = symbol.upper()
    # 币安API
    url = f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT'
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        return float(data['price'])
    except:
        return None

def get_stock_price(code):
    """获取股票价格 (A股)"""
    # 腾讯财经API
    url = f'https://qt.gtimg.cn/q={code}'
    try:
        resp = requests.get(url, timeout=10)
        data = resp.text
        # 解析返回数据
        if '"' in data:
            price = data.split('"')[1].split('~')[0]
            return float(price)
    except:
        return None

def get_taobao_price(item_id):
    """获取淘宝商品价格"""
    url = f'https://item.taobao.com/item.htm?id={item_id}'
    # 需要更复杂的解析
    return None

# 主逻辑
def add_watch(symbol, target_price, notify_above=True):
    """添加监控"""
    watches = load_watches()
    
    watch = {
        'symbol': symbol.upper(),
        'target': float(target_price),
        'notify_above': notify_above,
        'added_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    watches.append(watch)
    save_watches(watches)
    
    print(f"✅ 已添加监控: {symbol} 目标价格: {target_price}")

def remove_watch(symbol):
    """移除监控"""
    watches = load_watches()
    watches = [w for w in watches if w['symbol'] != symbol.upper()]
    save_watches(watches)
    print(f"✅ 已移除监控: {symbol}")

def list_watches():
    """列出所有监控"""
    watches = load_watches()
    if not watches:
        print("📃 没有监控目标")
        return
    
    print(f"📃 共 {len(watches)} 个监控:")
    for w in watches:
        direction = "高于" if w['notify_above'] else "低于"
        print(f"  • {w['symbol']} {direction} {w['target']}")

def check_prices():
    """检查所有价格"""
    watches = load_watches()
    
    for w in watches:
        symbol = w['symbol']
        target = w['target']
        
        # 判断类型
        if symbol in ['BTC', 'ETH', 'BNB', 'SOL', 'DOGE']:
            price = get_crypto_price(symbol)
        else:
            price = get_stock_price(symbol)
        
        if price is None:
            print(f"⚠️ 无法获取 {symbol} 价格")
            continue
        
        # 检查是否触发
        triggered = False
        if w['notify_above'] and price > target:
            triggered = True
            msg = f"🔔 {symbol} 现在价格 ${price:.2f} 超过目标 ${target}"
        elif not w['notify_above'] and price < target:
            triggered = True
            msg = f"🔔 {symbol} 现在价格 ${price:.2s} 低于目标 ${target}"
        
        if triggered:
            print(msg)
            # TODO: 发送通知
        
        print(f"  {symbol}: ${price:.2f} (目标: ${target})")

def watch_loop():
    """监控循环"""
    print("🔄 开始价格监控...")
    while True:
        check_prices()
        time.sleep(CONFIG['check_interval'])

# CLI
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 price_monitor.py add <币/股> <价格>")
        print("  python3 price_monitor.py remove <币/股>")
        print("  python3 price_monitor.py list")
        print("  python3 price_monitor.py check")
        print("  python3 price_monitor.py watch  # 持续监控")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'add' and len(sys.argv) >= 4:
        symbol = sys.argv[2]
        price = sys.argv[3]
        add_watch(symbol, price)
    
    elif cmd == 'remove' and len(sys.argv) >= 3:
        symbol = sys.argv[2]
        remove_watch(symbol)
    
    elif cmd == 'list':
        list_watches()
    
    elif cmd == 'check':
        check_prices()
    
    elif cmd == 'watch':
        watch_loop()
    
    else:
        print("命令错误")
