#!/usr/bin/env python3
"""
案例03: 天气早报
"""

class WeatherReport:
    def __init__(self):
        self.location = '北京'
    
    def generate(self):
        print(f"\n🌤️ {self.location} 天气早报")
        print(f"  天气: 晴")
        print(f"  温度: 15-25°C")
        print(f"  建议: 适合外出")


if __name__ == '__main__':
    r = WeatherReport()
    r.generate()
