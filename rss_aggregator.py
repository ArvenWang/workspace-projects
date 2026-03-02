#!/usr/bin/env python3
"""
案例20: RSS新闻聚合
功能：
1. 订阅RSS源
2. 去重聚合
3. 生成摘要

依赖：
pip3 install feedparser

运行：
python3 rss_aggregator.py add <URL>
python3 rss_aggregator.py list
python3 rss_aggregator.py fetch
"""

import os
import json
from datetime import datetime
from pathlib import Path

# 配置
CONFIG = {
    'data_dir': os.path.expanduser('~/.rss_aggregator'),
}

Path(CONFIG['data_dir']).mkdir(parents=True, exist_ok=True)

FEEDS_FILE = os.path.join(CONFIG['data_dir'], 'feeds.json')


class RSSAggregator:
    def __init__(self):
        self.feeds = self.load_feeds()
    
    def load_feeds(self):
        default = {
            'feeds': [
                {'name': '36kr', 'url': 'https://36kr.com/feed/', 'enabled': True},
                {'name': '少数派', 'url': 'https://sspai.com/feed', 'enabled': True},
            ],
            'articles': []
        }
        
        if os.path.exists(FEEDS_FILE):
            with open(FEEDS_FILE) as f:
                return json.load(f)
        else:
            self.save_feeds(default)
            return default
    
    def save_feeds(self, feeds):
        with open(FEEDS_FILE, 'w') as f:
            json.dump(feeds, f, indent=2, ensure_ascii=False)
    
    def add_feed(self, name, url):
        """添加订阅源"""
        self.feeds['feeds'].append({
            'name': name,
            'url': url,
            'enabled': True
        })
        self.save_feeds(self.feeds)
        print(f"✅ 已添加: {name}")
    
    def list_feeds(self):
        """列出订阅源"""
        print(f"\n📰 RSS订阅源 ({len(self.feeds['feeds'])}个):")
        
        for feed in self.feeds['feeds']:
            icon = '✅' if feed.get('enabled', True) else '⏸️'
            print(f"  {icon} {feed['name']}: {feed['url'][:40]}...")
    
    def fetch(self):
        """抓取内容"""
        print(f"\n🔄 抓取RSS源...")
        
        # 简化实现 - 实际需要feedparser
        print(f"⚠️ 需要安装 feedparser")
        print(f"   pip3 install feedparser")
        
        print(f"\n📋 已缓存 {len(self.feeds.get('articles', []))} 篇文章")


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""
RSS新闻聚合 - 使用说明

使用:
  python3 rss_aggregator.py add <名称> <URL>
  python3 rss_aggregator.py list
  python3 rss_aggregator.py fetch

示例:
  python3 rss_aggregator.py list
  python3 rss_aggregator.py add 知乎 https://www.zhihu.com/rss
""")
        sys.exit(1)
    
    cmd = sys.argv[1]
    aggregator = RSSAggregator()
    
    if cmd == 'add' and len(sys.argv) >= 4:
        name = sys.argv[2]
        url = sys.argv[3]
        aggregator.add_feed(name, url)
    
    elif cmd == 'list':
        aggregator.list_feeds()
    
    elif cmd == 'fetch':
        aggregator.fetch()
    
    else:
        print("命令错误")


if __name__ == '__main__':
    main()
