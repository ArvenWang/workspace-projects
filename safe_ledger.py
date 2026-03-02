#!/usr/bin/env python3
"""
案例42: 安全操作账本
功能：
1. 记录权限操作
2. 审计追踪
"""

class SafeLedger:
    def __init__(self):
        self.operations = []
    
    def log(self, operation, user, scope):
        self.operations.append({
            'time': 'now',
            'operation': operation,
            'user': user,
            'scope': scope
        })
    
    def show(self):
        print("\n📒 安全操作账本")
        print("="*50)
        
        for op in self.operations:
            print(f"  {op['time']} | {op['user']} | {op['operation']} | {op['scope']}")


if __name__ == '__main__':
    ledger = SafeLedger()
    ledger.log('读取', 'agent', 'file_system')
    ledger.log('执行', 'agent', 'shell')
    ledger.show()
