#!/usr/bin/env python3
"""
案例09: SSH密钥扫描
功能：
1. 扫描泄露的SSH密钥
2. 检查公钥私钥
3. 验证密钥安全性

运行：
python3 ssh_key_scanner.py scan
python3 ssh_key_scanner.py check <路径>
"""

import os
import re
from pathlib import Path
from datetime import datetime

# 配置
CONFIG = {
    'search_paths': [
        '~/.ssh',
        '~/.github',
    ],
    'data_dir': '~/.ssh_key_scanner',
}


class SSHKeyScanner:
    def __init__(self):
        self.findings = []
    
    def scan_path(self, path):
        """扫描路径"""
        path = os.path.expanduser(path)
        
        if not os.path.exists(path):
            return []
        
        results = []
        
        for root, dirs, files in os.walk(path):
            for f in files:
                filepath = os.path.join(root, f)
                
                # 检查私钥
                if f in ['id_rsa', 'id_dsa', 'id_ecdsa', 'id_ed25519']:
                    results.append({
                        'type': 'private_key',
                        'file': filepath,
                        'name': f
                    })
                
                # 检查公钥
                elif f.endswith('.pub'):
                    results.append({
                        'type': 'public_key',
                        'file': filepath,
                        'name': f
                    })
                
                # 检查known_hosts
                elif f == 'known_hosts':
                    results.append({
                        'type': 'known_hosts',
                        'file': filepath,
                        'name': f
                    })
        
        return results
    
    def scan(self):
        """扫描所有路径"""
        print(f"\n🔍 SSH密钥扫描")
        print("="*50)
        
        all_findings = []
        
        for path in CONFIG['search_paths']:
            findings = self.scan_path(path)
            
            if findings:
                print(f"\n📁 {path}:")
                for f in findings:
                    icon = {'private_key': '🔑', 'public_key': '🔓', 'known_hosts': '📋'}.get(f['type'], '❓')
                    print(f"  {icon} {f['name']} ({f['type']})")
                    all_findings.append(f)
        
        print("="*50)
        print(f"\n✅ 扫描完成: 发现 {len(all_findings)} 个文件")
        
        return all_findings
    
    def check_permissions(self, filepath):
        """检查文件权限"""
        if not os.path.exists(filepath):
            return None
        
        stat = os.stat(filepath)
        mode = stat.st_mode & 0o777
        
        # 私钥应该是600
        if 'id_rsa' in filepath or 'id_ed' in filepath:
            if mode == 0o600:
                return '✅ 安全'
            else:
                return f'⚠️ 权限过松: {oct(mode)}'
        
        return None


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""
SSH密钥扫描 - 使用说明

使用:
  python3 ssh_key_scanner.py scan     # 扫描
  python3 ssh_key_scanner.py check <路径>  # 检查

示例:
  python3 ssh_key_scanner.py scan
  python3 ssh_key_scanner.py check ~/.ssh/id_rsa
""")
        sys.exit(1)
    
    cmd = sys.argv[1]
    scanner = SSHKeyScanner()
    
    if cmd == 'scan':
        scanner.scan()
    
    elif cmd == 'check' and len(sys.argv) >= 3:
        path = os.path.expanduser(sys.argv[2])
        result = scanner.check_permissions(path)
        if result:
            print(result)
        else:
            print("无法检查")
    
    else:
        print("命令错误")


if __name__ == '__main__':
    main()
