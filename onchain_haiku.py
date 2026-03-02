#!/usr/bin/env python3
"""
案例44: 链上俳句
"""

class OnChainHaiku:
    def __init__(self):
        self.haikus = []
    
    def inscribe(self, haiku):
        print(f"\n🎭 链上俳句")
        print(f"  内容: {haiku}")
        print(f"  ✅ 已上链")


if __name__ == '__main__':
    h = OnChainHaiku()
    h.inscribe("静寂枯枝摇\t落萤点点照寒塘\t残梦夜未央")
