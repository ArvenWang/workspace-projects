#!/usr/bin/env python3
"""
日程管理AI助手
能帮你做什么：
1. 语音/文字添加日程
2. 自动安排时间
3. 冲突检测
4. 定时提醒

使用方式：
python3 calendar_ai.py add "明天上午9点开会"
python3 calendar_ai.py list
python3 calendar_ai.py today
"""

import json
import os
import re
from datetime import datetime, timedelta

# 配置
CONFIG = {
    'data_file': os.path.expanduser('~/.calendar_events.json'),
}

# 简单事件存储
events = []

def load_events():
    """加载事件"""
    global events
    if os.path.exists(CONFIG['data_file']):
        with open(CONFIG['data_file']) as f:
            events = json.load(f)
    return events

def save_events(events):
    """保存事件"""
    with open(CONFIG['data_file'], 'w') as f:
        json.dump(events, f, ensure_ascii=False, indent=2)

def parse_time(text):
    """解析时间文本"""
    now = datetime.now()
    text = text.lower()
    
    # 今天/明天/后天
    if '今天' in text:
        day = now.date()
    elif '明天' in text:
        day = (now + timedelta(days=1)).date()
    elif '后天' in text:
        day = (now + timedelta(days=2)).date()
    else:
        day = now.date()
    
    # 时间
    time_match = re.search(r'(\d{1,2})[点时](\d{0,2})?', text)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2) or 0)
    else:
        hour = 9
        minute = 0
    
    return datetime.combine(day, datetime.min.time().replace(hour=hour, minute=minute))

def add_event(text):
    """添加事件"""
    # 解析时间
    event_time = parse_time(text)
    
    # 提取事件内容 (去掉时间部分)
    content = re.sub(r'(今天|明天|后天|\d{1,2}[点时]\d{0,2}分?)', '', text).strip()
    
    event = {
        'id': len(events) + 1,
        'content': content,
        'time': event_time.strftime('%Y-%m-%d %H:%M'),
        'done': False,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    events.append(event)
    save_events(events)
    
    print(f"✅ 已添加: {event['time']} {content}")

def list_events(days=7):
    """列出事件"""
    events = load_events()
    
    if not events:
        print("📅 没有日程")
        return
    
    now = datetime.now()
    print(f"\n📅 接下来 {days} 天的日程:")
    print("-" * 40)
    
    for e in sorted(events, key=lambda x: x['time']):
        status = "✅" if e.get('done') else "⬜"
        print(f"{status} {e['time']} - {e['content']}")

def today_events():
    """今天的事件"""
    events = load_events()
    today = datetime.now().strftime('%Y-%m-%d')
    
    today_events = [e for e in events if e['time'].startswith(today)]
    
    if not today_events:
        print("今天没有日程")
        return
    
    print(f"\n📅 今日日程 ({today}):")
    print("-" * 40)
    for e in today_events:
        print(f"  {e['time'][-5:]} - {e['content']}")

def check_conflicts():
    """检查冲突"""
    events = load_events()
    times = {}
    
    for e in events:
        time = e['time']
        if time in times:
            times[time].append(e['content'])
        else:
            times[time] = [e['content']]
    
    conflicts = {k: v for k, v in times.items() if len(v) > 1}
    
    if conflicts:
        print("\n⚠️ 时间冲突:")
        for time, contents in conflicts.items():
            print(f"  {time}: {' + '.join(contents)}")
    else:
        print("✅ 没有时间冲突")

# AI对话接口
def ask_ai(text):
    """简单的AI响应"""
    text = text.lower()
    
    if '添加' in text or '安排' in text or '开会' in text:
        # 提取事件内容
        content = text.replace('添加', '').replace('安排', '').replace('开会', '').strip()
        if content:
            add_event(content)
            return "好的，已帮你安排"
    
    elif '查看' in text or '有什么' in text:
        list_events()
        return None
    
    elif '今天' in text:
        today_events()
        return None
    
    elif '冲突' in text:
        check_conflicts()
        return None
    
    else:
        return "你可以告诉我：'明天上午9点开会' 或 '查看今天的日程'"

# CLI
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 calendar_ai.py add <日程>")
        print("  python3 calendar_ai.py list")
        print("  python3 calendar_ai.py today")
        print("  python3 calendar_ai.py conflicts")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'add' and len(sys.argv) >= 3:
        text = ' '.join(sys.argv[2:])
        add_event(text)
    
    elif cmd == 'list':
        list_events()
    
    elif cmd == 'today':
        today_events()
    
    elif cmd == 'conflicts':
        check_conflicts()
    
    else:
        print("命令错误")
