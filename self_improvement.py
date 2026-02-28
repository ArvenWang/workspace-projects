#!/usr/bin/env python3
"""
案例39: 每日自我提升
功能：
1. 每天进步1%
2. 记录学习
3. 追踪成长

运行：
python3 self_improvement.py log <内容>
python3 self_improvement.py stats
python3 self_improvement.py today
"""

import os
import json
from datetime import datetime
from pathlib import Path

CONFIG = {
    'data_dir': os.path.expanduser('~/.self_improvement'),
}

Path(CONFIG['data_dir']).mkdir(parents=True, exist_ok=True)

LOG_FILE = os.path.join(CONFIG['data_dir'], 'log.json')


class SelfImprovement:
    def __init__(self):
        self.logs = self.load_logs()
    
    def load_logs(self):
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE) as f:
                return json.load(f)
        return []
    
    def save_logs(self):
        with open(LOG_FILE, 'w') as f:
            json.dump(self.logs, f, indent=2, ensure_ascii=False)
    
    def log(self, content):
        """记录学习"""
        entry = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M'),
            'content': content,
            'tags': self.extract_tags(content)
        }
        
        self.logs.append(entry)
        self.save_logs()
        
        print(f"✅ 已记录: {content[:50]}...")
    
    def extract_tags(self, content):
        """提取标签"""
        tags = []
        keywords = ['学习', '实践', '代码', '阅读', '视频', '课程']
        
        for kw in keywords:
            if kw in content:
                tags.append(kw)
        
        return tags
    
    def today(self):
        """今日记录"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        today_logs = [l for l in self.logs if l['date'] == today]
        
        print(f"\n📈 今日成长 - {today}")
        print("="*40)
        
        if not today_logs:
            print("暂无记录")
            return
        
        for log in today_logs:
            print(f"  {log['time']} - {log['content']}")
    
    def stats(self):
        """统计"""
        if not self.logs:
            print("暂无记录")
            return
        
        # 连续天数
        dates = list(set([l['date'] for l in self.logs]))
        dates.sort()
        
        print(f"\n📊 成长统计")
        print("="*40)
        print(f"  总记录: {len(self.logs)}条")
        print(f"  活跃天数: {len(dates)}天")
        
        if dates:
            print(f"  开始: {dates[0]}")
            print(f"  最近: {dates[-1]}")


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""
每日自我提升 - 使用说明

使用:
  python3 self_improvement.py log <内容>
  python3 self_improvement.py today
  python3 self_improvement.py stats

示例:
  python3 self_improvement.py log "学习了新的Python库"
  python3 self_improvement.py today
  python3 self_improvement.py stats
""")
        sys.exit(1)
    
    cmd = sys.argv[1]
    app = SelfImprovement()
    
    if cmd == 'log' and len(sys.argv) >= 3:
        content = ' '.join(sys.argv[2:])
        app.log(content)
    
    elif cmd == 'today':
        app.today()
    
    elif cmd == 'stats':
        app.stats()
    
    else:
        print("命令错误")


if __name__ == '__main__':
    main()
