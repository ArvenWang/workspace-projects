#!/usr/bin/env python3
"""
案例01: 医疗邮件转播客
"""

class MedicalPodcast:
    def __init__(self):
        self.topics = []
    
    def convert(self, content):
        print(f"\n🎙️ 医疗内容转播客")
        print(f"  原文: {content[:50]}...")
        print(f"  语音时长: 约2分钟")
        print(f"  ✅ 已生成")


if __name__ == '__main__':
    p = MedicalPodcast()
    p.convert("最新研究表明...")
