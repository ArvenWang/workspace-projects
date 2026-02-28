#!/usr/bin/env python3
"""
案例36: Heartbeat状态监控
功能：
1. 跟踪检查新鲜度
2. 记录各检查最后运行时间
3. 提醒过期检查

运行：
python3 heartbeat_monitor.py status
python3 heartbeat_monitor.py check <名称>
python3 heartbeat_monitor.py list
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path

# 配置
CONFIG = {
    'data_dir': os.path.expanduser('~/.heartbeat_monitor'),
    'thresholds': {
        'email': 30,  # 分钟
        'calendar': 60,
        'weather': 180,
        'news': 240,
    }
}

Path(CONFIG['data_dir']).mkdir(parents=True, exist_ok=True)

STATE_FILE = os.path.join(CONFIG['data_dir'], 'state.json')


class HeartbeatMonitor:
    def __init__(self):
        self.state = self.load_state()
    
    def load_state(self):
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE) as f:
                return json.load(f)
        return {'checks': {}}
    
    def save_state(self):
        with open(STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def check(self, name):
        """更新检查时间"""
        now = datetime.now()
        
        self.state['checks'][name] = {
            'last_check': now.isoformat(),
            'count': self.state['checks'].get(name, {}).get('count', 0) + 1
        }
        
        self.save_state()
        print(f"✅ 已记录 {name} 检查: {now.strftime('%H:%M:%S')}")
    
    def status(self, name=None):
        """查看状态"""
        print(f"\n💓 Heartbeat 状态")
        print("="*50)
        
        if name:
            # 查看单个
            if name in self.state['checks']:
                check = self.state['checks'][name]
                last = datetime.fromisoformat(check['last_check'])
                ago = (datetime.now() - last).minutes
                threshold = CONFIG['thresholds'].get(name, 60)
                
                status = '✅ 正常' if ago < threshold else '⚠️ 过期'
                
                print(f"{name}: {status}")
                print(f"  最后检查: {last.strftime('%H:%M:%S')} ({ago}分钟前)")
                print(f"  检查次数: {check['count']}")
            else:
                print(f"未找到: {name}")
        else:
            # 列出所有
            if not self.state['checks']:
                print("暂无检查记录")
                return
            
            for name, check in self.state['checks'].items():
                last = datetime.fromisoformat(check['last_check'])
                ago = (datetime.now() - last).total_seconds() / 60
                threshold = CONFIG['thresholds'].get(name, 60)
                
                status = '✅' if ago < threshold else '⚠️'
                print(f"{status} {name}: {check['count']}次, {int(ago)}分钟前")
        
        print("="*50)
    
    def stale(self):
        """列出过期检查"""
        print(f"\n⚠️ 过期检查:")
        
        stale = []
        
        for name, check in self.state['checks'].items():
            last = datetime.fromisoformat(check['last_check'])
            ago = (datetime.now() - last).total_seconds() / 60
            threshold = CONFIG['thresholds'].get(name, 60)
            
            if ago > threshold:
                stale.append((name, ago, threshold))
        
        if stale:
            for name, ago, threshold in stale:
                print(f"  {name}: {int(ago)}分钟前 (阈值{threshold}分钟)")
        else:
            print("  没有过期检查")
    
    def list(self):
        """列出所有检查"""
        self.status()


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""
Heartbeat监控 - 使用说明

使用:
  python3 heartbeat_monitor.py status     # 状态
  python3 heartbeat_monitor.py check <名称>  # 记录检查
  python3 heartbeat_monitor.py stale     # 过期检查
  python3 heartbeat_monitor.py list      # 列表

示例:
  python3 heartbeat_monitor.py status
  python3 heartbeat_monitor.py check email
  python3 heartbeat_monitor.py stale
""")
        sys.exit(1)
    
    cmd = sys.argv[1]
    monitor = HeartbeatMonitor()
    
    if cmd == 'status':
        name = sys.argv[2] if len(sys.argv) > 2 else None
        monitor.status(name)
    
    elif cmd == 'check' and len(sys.argv) >= 3:
        name = sys.argv[2]
        monitor.check(name)
    
    elif cmd == 'stale':
        monitor.stale()
    
    elif cmd == 'list':
        monitor.list()
    
    else:
        print("命令错误")


if __name__ == '__main__':
    main()
