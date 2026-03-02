#!/usr/bin/env python3
"""
案例04: 三层记忆系统(完整版)
"""

class ThreeTierMemory:
    def __init__(self):
        self.long_term = []  # 长期记忆
        self.working = []    # 工作记忆
        self.episodic = []  # 情景记忆
    
    def store_long_term(self, info):
        self.long_term.append(info)
        print(f"✅ 存入长期记忆: {info}")
    
    def store_working(self, info):
        self.working.append(info)
        print(f"📝 存入工作记忆: {info}")
    
    def store_episodic(self, event):
        self.episodic.append(event)
        print(f"📸 存入情景记忆: {event}")
    
    def recall(self, query):
        print(f"\n🔍 回忆: {query}")
        
        for m in self.long_term:
            if query in m:
                print(f"  找到: {m}")
    
    def consolidate(self):
        """将工作记忆转入长期记忆"""
        for info in self.working:
            self.long_term.append(info)
        self.working = []
        print("✅ 已整合到长期记忆")


if __name__ == '__main__':
    m = ThreeTierMemory()
    m.store_long_term("我是AI助手")
    m.store_working("用户问天气")
    m.recall("AI")
    m.consolidate()
