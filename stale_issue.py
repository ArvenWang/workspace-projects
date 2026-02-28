#!/usr/bin/env python3
"""
案例17: GitHub陈旧Issue清理
"""

class StaleIssueCleaner:
    def __init__(self):
        self.issues = []
    
    def find_stale(self):
        print("\n🧹 查找陈旧Issue")
        
        stale = [
            {'id': 1, 'title': 'Bug报告', 'days': 180},
            {'id': 2, 'title': '功能请求', 'days': 365},
        ]
        
        print(f"  发现 {len(stale)} 个陈旧Issue")
        
        return stale


if __name__ == '__main__':
    c = StaleIssueCleaner()
    c.find_stale()
