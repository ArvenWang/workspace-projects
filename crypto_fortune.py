#!/usr/bin/env python3
"""
案例46: 加密饼干
"""

class CryptoFortune:
    def __init__(self):
        self.fortunes = [
            "今天适合学习新技能",
            "代码写得好，bug自然少",
            "保持好奇，持续学习"
        ]
    
    def get(self):
        import random
        f = random.choice(self.fortunes)
        print(f"\n🍪 加密饼干: {f}")


if __name__ == '__main__':
    c = CryptoFortune()
    c.get()
