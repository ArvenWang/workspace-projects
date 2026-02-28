#!/usr/bin/env python3
"""
案例13: 5AM基础设施健康检查
功能：
1. 服务器状态检查
2. 服务运行状态
3. 磁盘/内存/CPU
4. 告警通知

运行：
python3 health_check.py run
python3 health_check.py status
"""

import os
import json
import subprocess
import psutil
from datetime import datetime
from pathlib import Path

# 配置
CONFIG = {
    'data_dir': os.path.expanduser('~/.health_check'),
    'threshold': {
        'cpu': 80,  # %
        'memory': 80,  # %
        'disk': 90,  # %
    }
}

Path(CONFIG['data_dir']).mkdir(parents=True, exist_ok=True)

REPORT_FILE = os.path.join(CONFIG['data_dir'], 'report.json')


class HealthCheck:
    def __init__(self):
        self.results = []
    
    def check_cpu(self):
        """CPU检查"""
        cpu = psutil.cpu_percent(interval=1)
        status = 'ok' if cpu < CONFIG['threshold']['cpu'] else 'warning'
        
        return {
            'name': 'CPU',
            'value': f'{cpu}%',
            'threshold': f"{CONFIG['threshold']['cpu']}%",
            'status': status
        }
    
    def check_memory(self):
        """内存检查"""
        mem = psutil.virtual_memory()
        status = 'ok' if mem.percent < CONFIG['threshold']['memory'] else 'warning'
        
        return {
            'name': '内存',
            'value': f'{mem.percent}%',
            'threshold': f"{CONFIG['threshold']['memory']}%",
            'status': status
        }
    
    def check_disk(self):
        """磁盘检查"""
        disk = psutil.disk_usage('/')
        status = 'ok' if disk.percent < CONFIG['threshold']['disk'] else 'warning'
        
        return {
            'name': '磁盘',
            'value': f'{disk.percent}%',
            'threshold': f"{CONFIG['threshold']['disk']}%",
            'status': status
        }
    
    def check_processes(self):
        """关键进程检查"""
        critical = ['python', 'node', 'docker', 'nginx']
        results = []
        
        for proc in psutil.process_iter(['name', 'status']):
            try:
                if proc.info['name'] in critical:
                    results.append(proc.info['name'])
            except:
                pass
        
        return {
            'name': '关键进程',
            'value': f'{len(set(results))}个运行中',
            'status': 'ok' if results else 'warning'
        }
    
    def check_network(self):
        """网络检查"""
        net = psutil.net_io_counters()
        return {
            'name': '网络',
            'value': f'↓{net.bytes_recv/1024/1024:.1f}MB ↑{net.bytes_sent/1024/1024:.1f}MB',
            'status': 'ok'
        }
    
    def run(self):
        """执行健康检查"""
        print(f"\n{'='*50}")
        print(f"🏥 5AM 基础设施健康检查")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print('='*50)
        
        checks = [
            self.check_cpu,
            self.check_memory,
            self.check_disk,
            self.check_processes,
            self.check_network,
        ]
        
        issues = []
        
        for check in checks:
            result = check()
            self.results.append(result)
            
            icon = {'ok': '✅', 'warning': '⚠️', 'error': '❌'}.get(result['status'], '❓')
            print(f"{icon} {result['name']}: {result['value']}")
            
            if result['status'] != 'ok':
                issues.append(f"{result['name']}: {result['value']}")
        
        # 保存报告
        report = {
            'time': datetime.now().isoformat(),
            'results': self.results,
            'issues': issues
        }
        
        with open(REPORT_FILE, 'w') as f:
            json.dump(report, f, indent=2)
        
        print('='*50)
        
        if issues:
            print(f"\n⚠️ 发现 {len(issues)} 个问题:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"\n✅ 所有检查通过!")
        
        return issues
    
    def status(self):
        """查看最近状态"""
        if os.path.exists(REPORT_FILE):
            with open(REPORT_FILE) as f:
                report = json.load(f)
            
            print(f"\n📊 最近检查: {report['time'][:19]}")
            
            for r in report['results']:
                icon = {'ok': '✅', 'warning': '⚠️'}.get(r['status'], '❌')
                print(f"{icon} {r['name']}: {r['value']}")
        else:
            print("暂无检查记录")


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""
5AM健康检查 - 使用说明

使用:
  python3 health_check.py run     # 执行检查
  python3 health_check.py status # 查看状态

示例:
  python3 health_check.py run
  python3 health_check.py status
""")
        sys.exit(1)
    
    cmd = sys.argv[1]
    checker = HealthCheck()
    
    if cmd == 'run':
        checker.run()
    elif cmd == 'status':
        checker.status()
    else:
        print("命令错误")


if __name__ == '__main__':
    main()
