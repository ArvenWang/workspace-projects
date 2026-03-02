#!/usr/bin/env python3
"""
案例02: 奥运早报
"""

class OlympicsBriefing:
    def __init__(self):
        self.countries = ['中国', '美国', '日本']
    
    def generate(self):
        print("\n🏅 奥运早报")
        
        medals = {'中国': '3金2银', '美国': '2金3银', '日本': '1金2银'}
        
        for c, m in medals.items():
            print(f"  {c}: {m}")


if __name__ == '__main__':
    b = OlympicsBriefing()
    b.generate()
