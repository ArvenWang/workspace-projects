#!/usr/bin/env python3
"""
案例57: 学习日记
"""

class LearningJournal:
    def __init__(self):
        self.entries = []
    
    def add(self, topic, notes):
        self.entries.append({
            'topic': topic,
            'notes': notes,
            'time': 'now'
        })
        print(f"✅ 已记录: {topic}")
    
    def review(self):
        print("\n📓 学习日记回顾")
        for e in self.entries:
            print(f"  - {e['topic']}: {e['notes'][:30]}...")


if __name__ == '__main__':
    j = LearningJournal()
    j.add('Python', '学会了异步编程')
    j.add('AI', '理解了Transformer')
    j.review()
