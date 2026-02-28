#!/usr/bin/env python3
"""
案例49: Trello整理
功能：
1. 夜间看板维护
2. 自动归档
"""

class TrelloOrganizer:
    def __init__(self):
        self.cards = []
    
    def add_card(self, name, list_name):
        self.cards.append({
            'name': name,
            'list': list_name,
            'age': 0
        })
    
    def archive_old(self, days=30):
        """归档旧卡片"""
        old = [c for c in self.cards if c['age'] > days]
        
        print(f"\n📋 归档 {len(old)} 张旧卡片")
        
        self.cards = [c for c in self.cards if c['age'] <= days]
        
        return len(old)


if __name__ == '__main__':
    org = TrelloOrganizer()
    org.add_card('功能A', '进行中')
    org.add_card('功能B', '待处理')
    
    archived = org.archive_old(30)
    print(f"已归档: {archived}张")
