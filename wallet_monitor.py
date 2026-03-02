#!/usr/bin/env python3
"""
案例22: 链上钱包监控
"""

class WalletMonitor:
    def __init__(self):
        self.wallets = []
    
    def add(self, address, label):
        self.wallets.append({'address': address, 'label': label})
        print(f"✅ 已添加监控: {label}")
    
    def check(self):
        print("\n💰 钱包监控")
        
        for w in self.wallets:
            print(f"  {w['label']}: 检测中...")


if __name__ == '__main__':
    monitor = WalletMonitor()
    monitor.add('0x123...', '热钱包')
    monitor.check()
