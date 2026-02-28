#!/usr/bin/env python3
"""
案例61: 阅读列表
功能：
1. 保存链接
2. 周五汇总
"""

class ReadingList:
    def __init__(self):
        self.items = []
    
    def add(self, url, title=''):
        self.items.append({
            'url': url,
            'title': title,
            'added': 'today'
        })
    
    def weekly_digest(self):
        print("\n📚 本周阅读列表")
        print("="*40)
        
        if not self.items:
            print("  暂无")
            return
        
        for i, item in enumerate(self.items, 1):
            title = item['title'] or item['url']
            print(f"  {i}. {title[:50]}")


if __name__ == '__main__':
    rl = ReadingList()
    rl.add('https://github.com', 'GitHub')
    rl.weekly_digest()
