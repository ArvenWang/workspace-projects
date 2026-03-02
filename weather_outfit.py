#!/usr/bin/env python3
"""
案例58: 天气穿搭
功能：
1. 获取天气
2. 建议穿搭
"""

import requests

class WeatherOutfit:
    def __init__(self):
        self.clothes = {
            'hot': ['短袖', '短裤', '裙子'],
            'warm': ['长袖', '长裤', '薄外套'],
            'cool': ['毛衣', '牛仔裤', '外套'],
            'cold': ['羽绒服', '棉裤', '围巾']
        }
    
    def suggest(self, temp):
        """建议穿搭"""
        if temp >= 30:
            category = 'hot'
        elif temp >= 20:
            category = 'warm'
        elif temp >= 10:
            category = 'cool'
        else:
            category = 'cold'
        
        print(f"\n👔 穿搭建议 (温度: {temp}°C)")
        print("="*40)
        print(f"  推荐: {', '.join(self.clothes[category])}")
        
        if category == 'hot':
            print(f"  建议: 带防晒, 多喝水")
        elif category == 'cold':
            print(f"  建议: 注意保暖, 带手套")


if __name__ == '__main__':
    outfit = WeatherOutfit()
    outfit.suggest(25)
