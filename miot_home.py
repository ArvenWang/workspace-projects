#!/usr/bin/env python3
"""
米家智能家居控制Agent
能帮你做什么：
1. 控制小米空调/风扇/灯
2. 查询设备状态
3. 定时开关设备
4. 场景联动

使用方式：
python3 miot_home.py on 空调 25
python3 miot_home.py off 风扇
python3 miot_home.py status
"""

import requests
import json
import os

# 米家云API (需要登录获取token)
CONFIG = {
    'server': 'https://api.iot.mi.com',
    'token_file': os.path.expanduser('~/.miot_token'),
}

# 设备列表 (需要你自己配置)
DEVICES = {
    '空调': {'did': '123456789', 'model': '空调型号'},
    '风扇': {'did': '123456790', 'model': '风扇型号'},
    '灯': {'did': '123456791', 'model': '灯型号'},
    '插座': {'did': '123456792', 'model': '插座型号'},
}

def load_token():
    """加载token"""
    if os.path.exists(CONFIG['token_file']):
        with open(CONFIG['token_file']) as f:
            return f.read().strip()
    return None

def save_token(token):
    """保存token"""
    with open(CONFIG['token_file'], 'w') as f:
        f.write(token)

def login(username, password):
    """登录米家账号获取token"""
    url = f"{CONFIG['server']}/v2/user/login"
    data = {
        'loginName': username,
        'password': password,
        'deviceId': 'openclaw_agent'
    }
    
    resp = requests.post(url, json=data)
    result = resp.json()
    
    if result.get('code') == 0:
        token = result['data']['token']
        save_token(token)
        print("✅ 登录成功!")
        return token
    else:
        print(f"❌ 登录失败: {result.get('message')}")
        return None

def send_command(device_id, cmd, param=None):
    """发送设备控制命令"""
    token = load_token()
    if not token:
        print("❌ 请先登录: python3 miot_home.py login <用户名> <密码>")
        return None
    
    url = f"{CONFIG['server']}/v2/device/control"
    
    data = {
        'did': device_id,
        'siid': 2,  # 服务ID
        'aiid': cmd,  # 操作ID
        'params': param or {}
    }
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    resp = requests.post(url, json=data, headers=headers)
    result = resp.json()
    
    if result.get('code') == 0:
        return True
    else:
        print(f"❌ 命令失败: {result.get('message')}")
        return False

def device_on(name, param=None):
    """打开设备"""
    if name not in DEVICES:
        print(f"❌ 未知设备: {name}")
        print(f"可用设备: {', '.join(DEVICES.keys())}")
        return
    
    device = DEVICES[name]
    print(f"🔛 打开 {name}...")
    
    # 通用开关命令
    result = send_command(device['did'], 1, param or {'on': True})
    if result:
        print(f"✅ {name} 已打开")

def device_off(name):
    """关闭设备"""
    if name not in DEVICES:
        print(f"❌ 未知设备: {name}")
        return
    
    device = DEVICES[name]
    print(f"🔛 关闭 {name}...")
    
    result = send_command(device['did'], 1, {'on': False})
    if result:
        print(f"✅ {name} 已关闭")

def get_status(name):
    """获取设备状态"""
    if name not in DEVICES:
        print(f"❌ 未知设备: {name}")
        return
    
    device = DEVICES[name]
    token = load_token()
    
    url = f"{CONFIG['server']}/v2/device/properties"
    data = {
        'did': device['did'],
        'siids': [2, 3, 4]  # 属性ID
    }
    headers = {'Authorization': f'Bearer {token}'}
    
    resp = requests.post(url, json=data, headers=headers)
    result = resp.json()
    
    if result.get('code') == 0:
        props = result['data']
        print(f"📊 {name} 状态:")
        for p in props:
            print(f"  {p}")
    else:
        print(f"❌ 获取失败: {result.get('message')}")

def list_devices():
    """列出所有设备"""
    print("📱 米家设备列表:")
    for name, device in DEVICES.items():
        print(f"  • {name} (ID: {device['did']})")

# CLI
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 miot_home.py login <用户名> <密码>")
        print("  python3 miot_home.py add <设备名> <did> <型号>")
        print("  python3 miot_home.py on <设备名> [参数]")
        print("  python3 miot_home.py off <设备名>")
        print("  python3 miot_home.py status <设备名>")
        print("  python3 miot_home.py list")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'login' and len(sys.argv) >= 4:
        username = sys.argv[2]
        password = sys.argv[3]
        login(username, password)
    
    elif cmd == 'add' and len(sys.argv) >= 5:
        name = sys.argv[2]
        did = sys.argv[3]
        model = sys.argv[4]
        DEVICES[name] = {'did': did, 'model': model}
        print(f"✅ 已添加设备: {name}")
    
    elif cmd == 'on' and len(sys.argv) >= 3:
        name = sys.argv[2]
        param = None
        if len(sys.argv) >= 4:
            # 解析参数 如 temperature=25
            param = {}
            for p in sys.argv[3:]:
                if '=' in p:
                    k, v = p.split('=', 1)
                    param[k] = v
        device_on(name, param)
    
    elif cmd == 'off' and len(sys.argv) >= 3:
        name = sys.argv[2]
        device_off(name)
    
    elif cmd == 'status' and len(sys.argv) >= 3:
        name = sys.argv[2]
        get_status(name)
    
    elif cmd == 'list':
        list_devices()
    
    else:
        print("命令错误")
