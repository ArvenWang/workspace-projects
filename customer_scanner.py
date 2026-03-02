#!/usr/bin/env python3
"""
案例23: 客户信号扫描
"""

class CustomerSignalScanner:
    def __init__(self):
        self.channels = ['email', 'twitter', 'support']
    
    def scan(self):
        print("\n🔍 客户信号扫描")
        
        signals = [
            ('投诉', 2),
            ('表扬', 5),
            ('建议', 3),
        ]
        
        for signal, count in signals:
            print(f"  {signal}: {count}条")


if __name__ == '__main__':
    scanner = CustomerSignalScanner()
    scanner.scan()
