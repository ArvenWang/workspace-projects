#!/usr/bin/env python3
"""
案例45: 早间摘要生成
功能：
1. 汇总夜间活动
2. 生成早报
"""

import json
from datetime import datetime

class MorningDigest:
    def __init__(self):
        self.activities = []
    
    def add(self, activity):
        self.activities.append({
            'time': datetime.now().strftime('%H:%M'),
            'activity': activity
        })
    
    def generate(self):
        print(f"\n🌅 早间摘要 - {datetime.now().strftime('%Y-%m-%d')}")
        print("="*50)
        
        if not self.activities:
            print("  夜间无活动")
            return
        
        print(f"  昨晚活动 ({len(self.activities)}项):")
        for a in self.activities:
            print(f"    {a['time']} - {a['activity']}")


if __name__ == '__main__':
    digest = MorningDigest()
    digest.add("案例06 - 交易监控")
    digest.add("案例05 - Shell别名")
    digest.generate()
