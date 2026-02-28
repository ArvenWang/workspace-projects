#!/usr/bin/env python3
"""
案例06: 交易机器人监控(完整版)
"""

class TradingBotMonitor:
    def __init__(self):
        self.bots = {}
    
    def add_bot(self, name, strategy):
        self.bots[name] = {'strategy': strategy, 'status': 'running', 'pnl': 0}
        print(f"✅ 添加机器人: {name} ({strategy})")
    
    def status(self):
        print("\n🤖 交易机器人状态")
        for name, bot in self.bots.items():
            print(f"  {name}: {bot['status']} | PnL: {bot['pnl']}%")
    
    def restart(self, name):
        if name in self.bots:
            print(f"🔄 重启 {name}...")
            self.bots[name]['status'] = 'running'


if __name__ == '__main__':
    monitor = TradingBotMonitor()
    monitor.add_bot('BTC套利', '网格')
    monitor.add_bot('ETH趋势', '均线')
    monitor.status()
    monitor.restart('BTC套利')
