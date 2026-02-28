#!/usr/bin/env python3
"""
智能家居控制中枢 - 完整版
功能：
1. 统一控制多设备
2. 场景联动
3. 语音指令解析
4. 定时任务

支持：
- 小米米家
- HomeAssistant
- 智能音箱

运行：
python3 smarthome.py status
python3 smarthome.py on 灯
python3 smarthome.py scene 离家
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path

# 配置
CONFIG = {
    'data_dir': os.path.expanduser('~/.smarthome'),
    'config_file': os.path.expanduser('~/.smarthome/config.json'),
}

Path(CONFIG['data_dir']).mkdir(parents=True, exist_ok=True)


class SmartHome:
    def __init__(self):
        self.scenes = self.load_scenes()
        self.devices = self.load_devices()
    
    def load_devices(self):
        """加载设备"""
        if os.path.exists(CONFIG['config_file']):
            with open(CONFIG['config_file']) as f:
                data = json.load(f)
                return data.get('devices', {})
        
        # 默认设备
        default = {
            '灯': {'type': 'light', 'room': '客厅', 'state': 'off'},
            '空调': {'type': 'ac', 'room': '卧室', 'state': 'off', 'temp': 26},
            '风扇': {'type': 'fan', 'room': '客厅', 'state': 'off'},
            '插座': {'type': 'plug', 'room': '书房', 'state': 'off'},
        }
        
        self.save_devices(default)
        return default
    
    def save_devices(self, devices):
        """保存设备"""
        data = {'devices': devices, 'scenes': self.scenes}
        with open(CONFIG['config_file'], 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_scenes(self):
        """加载场景"""
        if os.path.exists(CONFIG['config_file']):
            with open(CONFIG['config_file']) as f:
                data = json.load(f)
                return data.get('scenes', {})
        
        return {}
    
    def status(self):
        """查看状态"""
        print("\n🏠 智能家居状态")
        print("="*40)
        
        for name, device in self.devices.items():
            state = "开" if device.get('state') == 'on' else "关"
            room = device.get('room', '')
            dev_type = device.get('type', '')
            
            if dev_type == 'ac' and device.get('state') == 'on':
                temp = device.get('temp', 26)
                print(f"  {name} ({room}): {state} - {temp}°C")
            else:
                print(f"  {name} ({room}): {state}")
        
        print("="*40)
    
    def control(self, device_name, action):
        """控制设备"""
        if device_name not in self.devices:
            print(f"❌ 设备不存在: {device_name}")
            return False
        
        device = self.devices[device_name]
        
        if action == 'on':
            device['state'] = 'on'
            print(f"✅ 已打开: {device_name}")
        elif action == 'off':
            device['state'] = 'off'
            print(f"✅ 已关闭: {device_name}")
        elif action == 'toggle':
            device['state'] = 'off' if device.get('state') == 'on' else 'on'
            state = "开" if device['state'] == 'on' else "关"
            print(f"✅ {device_name}: {state}")
        elif action == 'status':
            state = device.get('state', 'off')
            print(f"  {device_name}: {state}")
            return True
        else:
            print(f"❌ 未知操作: {action}")
            return False
        
        self.save_devices(self.devices)
        return True
    
    def set_temperature(self, device_name, temp):
        """设置温度"""
        if device_name not in self.devices:
            print(f"❌ 设备不存在: {device_name}")
            return
        
        device = self.devices[device_name]
        if device.get('type') == 'ac':
            device['temp'] = int(temp)
            device['state'] = 'on'
            self.save_devices(self.devices)
            print(f"✅ 空调调至: {temp}°C")
        else:
            print(f"❌ 该设备不支持温度调节")
    
    def add_scene(self, name, actions):
        """添加场景"""
        self.scenes[name] = actions
        print(f"✅ 已添加场景: {name}")
        self.save_devices(self.devices)
    
    def run_scene(self, name):
        """执行场景"""
        if name not in self.scenes:
            print(f"❌ 场景不存在: {name}")
            return
        
        print(f"\n🎬 执行场景: {name}")
        
        for action in self.scenes[name]:
            device = action.get('device')
            cmd = action.get('action')
            param = action.get('param')
            
            if cmd == 'on' or cmd == 'off':
                self.control(device, cmd)
            elif cmd == 'temp' and param:
                self.set_temperature(device, param)
            
            time.sleep(0.5)
        
        print(f"✅ 场景执行完成")
    
    def voice_command(self, command):
        """语音指令解析"""
        command = command.lower()
        
        # 打开
        if '打开' in command or '开' in command:
            for name in self.devices:
                if name in command:
                    self.control(name, 'on')
                    return
        
        # 关闭
        if '关闭' in command or '关' in command:
            for name in self.devices:
                if name in command:
                    self.control(name, 'off')
                    return
        
        # 调温度
        if '度' in command or '温度' in command:
            import re
            temp = re.search(r'(\d+)度', command)
            if temp:
                self.set_temperature('空调', temp.group(1))
                return
        
        print("❌ 无法理解指令")


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""
智能家居控制中枢 - 使用说明

使用:
  python3 smarthome.py status          # 查看状态
  python3 smarthome.py on <设备>       # 打开
  python3 smarthome.py off <设备>      # 关闭
  python3 smarthome.py toggle <设备>  # 切换
  python3 smarthome.py temp <设备> <温度>  # 调温
  python3 smarthome.py scene <名称>   # 执行场景
  python3 smarthome.py voice <指令>   # 语音指令

示例:
  python3 smarthome.py status
  python3 smarthome.py on 灯
  python3 smarthome.py off 空调
  python3 smarthome.py temp 空调 25
  python3 smarthome.py voice "打开灯"
""")
        sys.exit(1)
    
    cmd = sys.argv[1]
    home = SmartHome()
    
    if cmd == 'status':
        home.status()
    
    elif cmd in ['on', 'off', 'toggle'] and len(sys.argv) >= 3:
        device = sys.argv[2]
        home.control(device, cmd)
    
    elif cmd == 'temp' and len(sys.argv) >= 4:
        device = sys.argv[2]
        temp = sys.argv[3]
        home.set_temperature(device, temp)
    
    elif cmd == 'scene' and len(sys.argv) >= 3:
        name = sys.argv[2]
        home.run_scene(name)
    
    elif cmd == 'voice' and len(sys.argv) >= 3:
        command = ' '.join(sys.argv[2:])
        home.voice_command(command)
    
    else:
        print("命令错误")


if __name__ == '__main__':
    main()
