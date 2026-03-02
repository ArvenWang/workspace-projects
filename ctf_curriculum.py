#!/usr/bin/env python3
"""
案例43: 安全CTF课程
"""

class CTFCurriculum:
    def __init__(self):
        self.topics = []
    
    def generate(self):
        print("\n🔐 CTF课程")
        
        topics = [
            ('Web安全', '基础'),
            ('密码学', '中级'),
            ('逆向工程', '高级'),
        ]
        
        for t, level in topics:
            print(f"  {t}: {level}")


if __name__ == '__main__':
    c = CTFCurriculum()
    c.generate()
