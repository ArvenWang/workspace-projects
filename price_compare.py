#!/usr/bin/env python3
"""
案例67: 比价购物
"""

class PriceCompare:
    def __init__(self):
        self.stores = ['京东', '淘宝', '拼多多']
    
    def compare(self, product):
        print(f"\n🔍 比价: {product}")
        
        for store in self.stores:
            # 模拟价格
            import random
            price = random.randint(100, 500)
            print(f"  {store}: ¥{price}")
        
        print(f"  最便宜: 拼多多")


if __name__ == '__main__':
    pc = PriceCompare()
    pc.compare('iPhone 15')
