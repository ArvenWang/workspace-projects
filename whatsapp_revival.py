#!/usr/bin/env python3
"""
案例14: WhatsApp复活
"""

class WhatsAppRevival:
    def __init__(self):
        self.contacts = []
    
    def revive(self, contact, message):
        print(f"\n📱 WhatsApp复活")
        print(f"  发送给: {contact}")
        print(f"  内容: {message}")
        print(f"  ✅ 已发送")


if __name__ == '__main__':
    w = WhatsAppRevival()
    w.reive('张三', '最近怎么样？')
