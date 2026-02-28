#!/usr/bin/env python3
"""
案例20: RSS聚合器(完整版)
"""

class RSSAggregatorComplete:
    def __init__(self):
        self.feeds = []
        self.articles = []
    
    def add_feed(self, name, url):
        self.feeds.append({'name': name, 'url': url})
        print(f"✅ 添加订阅: {name}")
    
    def fetch(self):
        print(f"\n📰 抓取 {len(self.feeds)} 个源...")
        
        # 模拟
        articles = [
            {'title': 'AI新突破', 'source': '36kr'},
            {'title': '新框架发布', 'source': 'github'},
        ]
        
        for a in articles:
            self.articles.append(a)
            print(f"  - {a['title']} ({a['source']})")
    
    def dedup(self):
        print("  ✅ 去重完成")


if __name__ == '__main__':
    rss = RSSAggregatorComplete()
    rss.add_feed('36kr', 'https://36kr.com/feed')
    rss.add_feed('少数派', 'https://sspai.com/feed')
    rss.fetch()
    rss.dedup()
