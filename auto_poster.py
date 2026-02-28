#!/usr/bin/env python3
"""
案例65: 自动社媒发布
功能：
1. 定时发布内容
2. 多平台支持

运行：
python3 auto_poster.py add <平台> <内容>
python3 auto_poster.py list
"""

import json
import os
from datetime import datetime
from pathlib import Path

CONFIG = {'data_dir': os.path.expanduser('~/.auto_poster')}
Path(CONFIG['data_dir']).mkdir(parents=True, exist_ok=True)


class AutoPoster:
    def __init__(self):
        self.posts = self.load_posts()
    
    def load_posts(self):
        file = os.path.join(CONFIG['data_dir'], 'posts.json')
        if os.path.exists(file):
            with open(file) as f:
                return json.load(f)
        return []
    
    def save_posts(self):
        file = os.path.join(CONFIG['data_dir'], 'posts.json')
        with open(file, 'w') as f:
            json.dump(self.posts, f, indent=2)
    
    def add(self, platform, content):
        """添加发布任务"""
        post = {
            'platform': platform,
            'content': content,
            'created': datetime.now().isoformat(),
            'status': 'pending'
        }
        self.posts.append(post)
        self.save_posts()
        print(f"✅ 已添加: {platform} - {content[:30]}...")
    
    def list_posts(self):
        """列出任务"""
        if not self.posts:
            print("暂无发布任务")
            return
        
        print(f"\n📝 发布任务 ({len(self.posts)}个):")
        for p in self.posts:
            print(f"  [{p['platform']}] {p['content'][:40]}... - {p['status']}")


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""
自动发布 - 使用说明

使用:
  python3 auto_poster.py add <平台> <内容>
  python3 auto_poster.py list

示例:
  python3 auto_poster.py add twitter "Hello World"
  python3 auto_poster.py list
""")
        sys.exit(1)
    
    cmd = sys.argv[1]
    poster = AutoPoster()
    
    if cmd == 'add' and len(sys.argv) >= 4:
        platform = sys.argv[2]
        content = ' '.join(sys.argv[3:])
        poster.add(platform, content)
    
    elif cmd == 'list':
        poster.list_posts()
    
    else:
        print("命令错误")


if __name__ == '__main__':
    main()
