#!/usr/bin/env python3
"""
案例47: Agent技能目录
"""

class SkillsDirectory:
    def __init__(self):
        self.skills = {
            'browser': '浏览器自动化',
            'github': 'GitHub操作',
            'weather': '天气查询',
            'tts': '语音合成'
        }
    
    def list(self):
        print("\n📁 Agent技能目录")
        for name, desc in self.skills.items():
            print(f"  • {name}: {desc}")


if __name__ == '__main__':
    s = SkillsDirectory()
    s.list()
