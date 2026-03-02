#!/usr/bin/env python3
"""
案例55: 智能日历提醒
功能：
1. 上下文感知提醒
2. 准备建议
"""

class SmartReminder:
    def __init__(self):
        self.reminders = []
    
    def add(self, event, time):
        """添加提醒"""
        self.reminders.append({
            'event': event,
            'time': time
        })
    
    def suggest_prep(self, event):
        """准备建议"""
        suggestions = {
            '会议': ['准备材料', '提前5分钟进入'],
            '面试': ['复习简历', '准备问题'],
            '约会': ['提前到达', '注意形象']
        }
        
        for key, sugg in suggestions.items():
            if key in event:
                return sugg
        
        return ['按时参加']


if __name__ == '__main__':
    reminder = SmartReminder()
    reminder.add('会议讨论', '14:00')
    
    prep = reminder.suggest_prep('会议讨论')
    print("准备建议:", prep)
