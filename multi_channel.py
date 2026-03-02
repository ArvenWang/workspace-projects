#!/usr/bin/env python3
"""
案例50: 多渠道同步
"""

class MultiChannelSync:
    def __init__(self):
        self.channels = ['telegram', 'discord', 'feishu']
    
    def sync(self, message):
        print(f"\n🔄 同步消息到 {len(self.channels)} 个渠道:")
        
        for ch in self.channels:
            print(f"  → {ch}: 已发送")


if __name__ == '__main__':
    sync = MultiChannelSync()
    sync.sync("Hello!")
