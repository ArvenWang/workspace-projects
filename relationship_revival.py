#!/usr/bin/env python3
"""
案例54: 联系人复活
功能：
1. 找回疏远的朋友
2. 发送暖心消息
"""

class RelationshipRevival:
    def __init__(self):
        self.contacts = []
    
    def add(self, name, last_contact):
        self.contacts.append({
            'name': name,
            'last_contact': last_contact,
            'status': 'cold'
        })
    
    def find_cold(self):
        """找联系人"""
        cold = [c for c in self.contacts if c['status'] == 'cold']
        return cold
    
    def suggest_message(self, name):
        """建议消息"""
        templates = [
            f"Hi {name}，最近怎么样？想起你了！",
            f"{name}，好久不见了，最近好吗？",
            f"hey {name}，突然想到你，来聊聊~"
        ]
        
        print(f"\n💬 建议给 {name} 发送:")
        for i, t in enumerate(templates, 1):
            print(f"  {i}. {t}")


if __name__ == '__main__':
    rr = RelationshipRevival()
    rr.add('张三', '2024-01-01')
    rr.add('李四', '2023-06-01')
    
    cold = rr.find_cold()
    if cold:
        rr.suggest_message(cold[0]['name'])
