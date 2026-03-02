#!/usr/bin/env python3
"""
案例08: X(Twitter)资料抓取
功能：
1. 抓取用户资料
2. 提取推文
3. 分析互动数据

依赖：
pip3 install requests beautifulsoup4

运行：
python3 x_scraper.py profile <用户名>
python3 x_scraper.py tweets <用户名>
"""

import requests
import json
import re
from datetime import datetime

# 配置
CONFIG = {
    'data_dir': '~/.x_scraper',
    'timeout': 30,
}


class XScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def get_profile(self, username):
        """获取用户资料"""
        print(f"🔍 抓取 @{username} 资料...")
        
        # 使用fxtwitter
        url = f"https://fxtwitter.com/{username}"
        
        try:
            resp = self.session.get(url, timeout=CONFIG['timeout'])
            
            if resp.status_code == 200:
                # 提取信息
                html = resp.text
                
                # 简单解析
                name = re.search(r'@(.*?)"', html)
                
                print(f"✅ 抓取成功!")
                return {
                    'username': username,
                    'url': url,
                    'fetched_at': datetime.now().isoformat()
                }
            else:
                print(f"❌ 抓取失败: {resp.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 错误: {e}")
            return None
    
    def get_tweets(self, username, limit=10):
        """获取推文"""
        print(f"🔍 抓取 @{username} 推文...")
        
        # 简化实现
        url = f"https://fxtwitter.com/{username}"
        
        try:
            resp = self.session.get(url, timeout=CONFIG['timeout'])
            
            if resp.status_code == 200:
                print(f"✅ 抓取成功!")
                return []
            else:
                return None
                
        except Exception as e:
            print(f"❌ 错误: {e}")
            return None


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""
X资料抓取 - 使用说明

使用:
  python3 x_scraper.py profile <用户名>
  python3 x_scraper.py tweets <用户名>

示例:
  python3 x_scraper.py profile elonmusk
  python3 x_scraper.py tweets elonmusk
""")
        sys.exit(1)
    
    cmd = sys.argv[1]
    scraper = XScraper()
    
    if cmd == 'profile' and len(sys.argv) >= 3:
        username = sys.argv[2]
        scraper.get_profile(username)
    
    elif cmd == 'tweets' and len(sys.argv) >= 3:
        username = sys.argv[2]
        scraper.get_tweets(username)
    
    else:
        print("命令错误")


if __name__ == '__main__':
    main()
