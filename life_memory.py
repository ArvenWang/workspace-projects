#!/usr/bin/env python3
"""
案例60: 记忆记录
"""

class LifeMemory:
    def __init__(self):
        self.memories = []
    
    def remember(self, event, people=None):
        memory = {
            'event': event,
            'people': people or [],
            'date': 'today'
        }
        self.memories.append(memory)
        print(f"✅ 已记住: {event}")
    
    def recall(self, keyword):
        print(f"\n🔍 回忆: {keyword}")
        for m in self.memories:
            if keyword in m['event']:
                print(f"  - {m['event']}")


if __name__ == '__main__':
    m = LifeMemory()
    m.remember('张三的生日', ['张三'])
    m.recall('生日')
