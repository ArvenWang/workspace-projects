#!/usr/bin/env python3
"""
案例53: Instagram Story Manager
"""

class InstaManager:
    def __init__(self):
        self.stories = []
    
    def schedule(self, content, time):
        self.stories.append({'content': content, 'time': time})
        print(f"✅ 已安排: {content[:30]}... @ {time}")


if __name__ == '__main__':
    mgr = InstaManager()
    mgr.schedule("新功能发布", "10:00")
