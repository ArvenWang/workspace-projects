#!/usr/bin/env python3
"""
案例59: 新闻聚合
"""

class NewsAggregator:
    def __init__(self):
        self.sources = []
    
    def add_source(self, name, url):
        self.sources.append({'name': name, 'url': url})
    
    def fetch(self):
        print("\n📰 新闻聚合")
        
        news = [
            ('科技', 'AI取得新进展'),
            ('商业', '新政策发布'),
            ('国际', '峰会召开')
        ]
        
        for category, title in news:
            print(f"  [{category}] {title}")


if __name__ == '__main__':
    n = NewsAggregator()
    n.add_source('36kr', 'https://36kr.com')
    n.fetch()
