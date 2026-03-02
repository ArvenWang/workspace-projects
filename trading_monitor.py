#!/usr/bin/env python3
"""
案例06: 交易机器人监控
功能：
1. 监控交易机器人状态
2. 自动重启崩溃的机器人
3. 数据恢复
4. 异常告警

依赖：
pip3 install requests

运行：
python3 trading_monitor.py status
python3 trading_monitor.py restart
python3 trading_monitor.py check
"""

import os
import json
import time
import requests
from datetime import datetime
from pathlib import Path

# 配置
CONFIG = {
    'data_dir': os.path.expanduser('~/.trading_monitor'),
    'check_interval': 60,  # 1分钟检查一次
    'max_restart': 3,  # 最大重启次数
}

Path(CONFIG['data_dir']).mkdir(parents=True, exist_ok=True)

STATUS_FILE = os.path.join(CONFIG['data_dir'], 'status.json')
ALERT_FILE = os.path.join(CONFIG['data_dir'], 'alerts.json')


class TradingMonitor:
    def __init__(self):
        self.bots = self.load_bots()
        self.alerts = self.load_alerts()
    
    def load_bots(self):
        """加载机器人配置"""
        default = {
            'binance_future': {
                'name': 'Binance期货机器人',
                'type': 'futures',
                'status': 'running',
                'pid': None,
                'last_check': None,
                'restart_count': 0
            },
            'spot_trader': {
                'name': '现货交易机器人',
                'type': 'spot',
                'status': 'stopped',
                'pid': None,
                'last_check': None,
                'restart_count': 0
            }
        }
        
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE) as f:
                return json.load(f)
        else:
            self.save_bots(default)
            return default
    
    def save_bots(self, bots):
        with open(STATUS_FILE, 'w') as f:
            json.dump(bots, f, indent=2, ensure_ascii=False)
    
    def load_alerts(self):
        if os.path.exists(ALERT_FILE):
            with open(ALERT_FILE) as f:
                return json.load(f)
        return []
    
    def save_alerts(self):
        with open(ALERT_FILE, 'w') as f:
            json.dump(self.alerts, f, indent=2)
    
    # ===== 监控 =====
    
    def check_bot(self, bot_name):
        """检查机器人状态"""
        bot = self.bots.get(bot_name)
        if not bot:
            return None
        
        now = datetime.now().isoformat()
        bot['last_check'] = now
        
        # 模拟检查 - 实际应该检查进程/API
        # 这里返回状态
        return {
            'name': bot['name'],
            'status': bot['status'],
            'last_check': now,
            'restart_count': bot['restart_count']
        }
    
    def check_all(self):
        """检查所有机器人"""
        print(f"\n{'='*50}")
        print(f"🔍 交易机器人监控 - {datetime.now().strftime('%H:%M:%S')}")
        print('='*50)
        
        issues = []
        
        for name, bot in self.bots.items():
            status = self.check_bot(name)
            
            # 检查状态
            if bot['status'] == 'running':
                print(f"✅ {bot['name']}: 运行中")
            elif bot['status'] == 'stopped':
                print(f"⏹️ {bot['name']}: 已停止")
            elif bot['status'] == 'error':
                print(f"❌ {bot['name']}: 错误")
                issues.append(bot['name'])
            
            # 检查重启次数
            if bot['restart_count'] > CONFIG['max_restart']:
                print(f"⚠️ {bot['name']}: 重启次数过多 ({bot['restart_count']})")
                issues.append(f"{bot['name']}需要人工介入")
        
        if issues:
            print(f"\n⚠️ 发现 {len(issues)} 个问题需要处理")
        else:
            print(f"\n✅ 所有机器人正常")
        
        return issues
    
    def restart_bot(self, bot_name):
        """重启机器人"""
        if bot_name not in self.bots:
            print(f"❌ 机器人不存在: {bot_name}")
            return False
        
        bot = self.bots[bot_name]
        
        if bot['restart_count'] >= CONFIG['max_restart']:
            print(f"❌ 重启次数已达上限: {bot['restart_count']}")
            return False
        
        print(f"🔄 重启 {bot['name']}...")
        
        # 模拟重启 - 实际应该重启进程
        bot['status'] = 'running'
        bot['restart_count'] += 1
        self.save_bots(self.bots)
        
        print(f"✅ {bot['name']} 已重启 (第{bot['restart_count']}次)")
        return True
    
    def add_alert(self, message):
        """添加告警"""
        alert = {
            'time': datetime.now().isoformat(),
            'message': message
        }
        self.alerts.append(alert)
        self.save_alerts()
    
    def list_alerts(self):
        """列出告警"""
        if not self.alerts:
            print("✅ 没有告警")
            return
        
        print(f"\n📋 告警历史 ({len(self.alerts)}条):")
        for a in self.alerts[-10:]:
            print(f"  {a['time'][:19]} - {a['message']}")
    
    def status(self):
        """状态总览"""
        print(f"\n📊 交易机器人状态")
        print("="*50)
        
        for name, bot in self.bots.items():
            status_icon = {
                'running': '✅',
                'stopped': '⏹️',
                'error': '❌'
            }.get(bot['status'], '❓')
            
            print(f"\n{status_icon} {bot['name']}")
            print(f"   类型: {bot['type']}")
            print(f"   状态: {bot['status']}")
            print(f"   重启次数: {bot['restart_count']}")
            print(f"   最后检查: {bot.get('last_check', 'N/A')}")


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""
交易机器人监控 - 使用说明

使用:
  python3 trading_monitor.py status     # 查看状态
  python3 trading_monitor.py check     # 检查机器人
  python3 trading_monitor.py restart <名称>  # 重启
  python3 trading_monitor.py alerts    # 告警历史

示例:
  python3 trading_monitor.py status
  python3 trading_monitor.py check
  python3 trading_monitor.py restart binance_future
""")
        sys.exit(1)
    
    cmd = sys.argv[1]
    monitor = TradingMonitor()
    
    if cmd == 'status':
        monitor.status()
    
    elif cmd == 'check':
        monitor.check_all()
    
    elif cmd == 'restart' and len(sys.argv) >= 3:
        bot_name = sys.argv[2]
        monitor.restart_bot(bot_name)
    
    elif cmd == 'alerts':
        monitor.list_alerts()
    
    else:
        print("命令错误")


if __name__ == '__main__':
    main()
