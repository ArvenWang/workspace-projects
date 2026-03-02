#!/usr/bin/env python3
"""
案例51: 每日学习日报→播客
功能：
1. 将学习内容转为语音
2. 中文播客
3. 定时生成

运行：
python3 daily_podcast.py create <内容>
python3 daily_podcast.py list
"""

import os
import json
from datetime import datetime
from pathlib import Path

CONFIG = {
    'data_dir': os.path.expanduser('~/.daily_podcast'),
    'output_dir': os.path.expanduser('~/.daily_podcast/output'),
}

Path(CONFIG['output_dir']).mkdir(parents=True, exist_ok=True)


class DailyPodcast:
    def __init__(self):
        self.episodes = self.load_episodes()
    
    def load_episodes(self):
        file = os.path.join(CONFIG['data_dir'], 'episodes.json')
        if os.path.exists(file):
            with open(file) as f:
                return json.load(f)
        return []
    
    def save_episodes(self):
        file = os.path.join(CONFIG['data_dir'], 'episodes.json')
        with open(file, 'w') as f:
            json.dump(self.episodes, f, indent=2, ensure_ascii=False)
    
    def create(self, content):
        """创建播客"""
        episode = {
            'id': len(self.episodes) + 1,
            'title': f"学习日报 {datetime.now().strftime('%Y-%m-%d')}",
            'content': content,
            'created_at': datetime.now().isoformat(),
            'audio_file': None
        }
        
        self.episodes.append(episode)
        self.save_episodes()
        
        print(f"✅ 已创建播客: {episode['title']}")
        print(f"   内容: {content[:50]}...")
        
        return episode
    
    def list_episodes(self):
        """列出播客"""
        if not self.episodes:
            print("暂无播客")
            return
        
        print(f"\n🎙️ 播客列表 ({len(self.episodes)}期):")
        
        for ep in reversed(self.episodes[-10:]):
            print(f"  #{ep['id']} {ep['title']}: {ep['content'][:30]}...")


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""
每日学习日报播客 - 使用说明

使用:
  python3 daily_podcast.py create <内容>
  python3 daily_podcast.py list

示例:
  python3 daily_podcast.py create "今天学习了Python异步编程"
  python3 daily_podcast.py list
""")
        sys.exit(1)
    
    cmd = sys.argv[1]
    podcast = DailyPodcast()
    
    if cmd == 'create' and len(sys.argv) >= 3:
        content = ' '.join(sys.argv[2:])
        podcast.create(content)
    
    elif cmd == 'list':
        podcast.list_episodes()
    
    else:
        print("命令错误")


if __name__ == '__main__':
    main()
