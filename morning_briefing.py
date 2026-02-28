#!/usr/bin/env python3
"""
案例52: 每日早报
功能：
1. 天气信息
2. 日程
3. 新闻摘要
4. 定时推送

运行：
python3 morning_briefing.py now
python3 morning_briefing.py schedule
"""

import os
import json
from datetime import datetime
from pathlib import Path

CONFIG = {
    'data_dir': os.path.expanduser('~/.morning_briefing'),
}

Path(CONFIG['data_dir']).mkdir(parents=True, exist_ok=True)


class MorningBriefing:
    def __init__(self):
        self.config = self.load_config()
    
    def load_config(self):
        file = os.path.join(CONFIG['data_dir'], 'config.json')
        default = {
            'include_weather': True,
            'include_calendar': True,
            'include_news': True,
            'send_to': 'telegram'  # telegram/feishu
        }
        
        if os.path.exists(file):
            with open(file) as f:
                return json.load(f)
        
        with open(file, 'w') as f:
            json.dump(default, f, indent=2)
        
        return default
    
    def get_weather(self):
        """获取天气"""
        # 简化实现
        return "北京: 晴 15-25°C"
    
    def get_calendar(self):
        """获取日程"""
        return ["9:00 会议", "14:00 汇报"]
    
    def get_news(self):
        """获取新闻"""
        return ["新闻1", "新闻2"]
    
    def generate(self):
        """生成早报"""
        print(f"\n{'='*50}")
        print(f"📰 每日早报 - {datetime.now().strftime('%Y-%m-%d')}")
        print('='*50)
        
        if self.config.get('include_weather'):
            print(f"\n🌤️ 天气:")
            print(f"   {self.get_weather()}")
        
        if self.config.get('include_calendar'):
            print(f"\n📅 日程:")
            for event in self.get_calendar():
                print(f"   • {event}")
        
        if self.config.get('include_news'):
            print(f"\n📰 新闻:")
            for news in self.get_news():
                print(f"   • {news}")
        
        print(f"\n{'='*50}")
    
    def now(self):
        """立即生成"""
        self.generate()


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""
每日早报 - 使用说明

使用:
  python3 morning_briefing.py now       # 立即生成
  python3 morning_briefing.py schedule  # 定时任务

示例:
  python3 morning_briefing.py now
""")
        sys.exit(1)
    
    cmd = sys.argv[1]
    briefing = MorningBriefing()
    
    if cmd == 'now':
        briefing.now()
    elif cmd == 'schedule':
        print("设置定时任务: crontab -e")
        print("0 7 * * * python3 /path/to/morning_briefing.py now")
    else:
        print("命令错误")


if __name__ == '__main__':
    main()
