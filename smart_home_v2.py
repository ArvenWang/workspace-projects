#!/usr/bin/env python3
"""
案例62: 智能家居(完整版)
"""

class SmartHome:
    def __init__(self):
        self.devices = {}
    
    def add_device(self, name, room):
        self.devices[name] = {'room': room, 'on': False}
        print(f"✅ 添加设备: {name} ({room})")
    
    def control(self, name, action):
        if name in self.devices:
            self.devices[name]['on'] = action == 'on'
            state = "开" if action == 'on' else "关"
            print(f"✅ {name} 已{state}")
        else:
            print(f"❌ 设备不存在")


if __name__ == '__main__':
    home = SmartHome()
    home.add_device('灯', '客厅')
    home.add_device('空调', '卧室')
    home.control('灯', 'on')
    home.control('空调', 'off')
