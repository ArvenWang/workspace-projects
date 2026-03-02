#!/usr/bin/env python3
"""
案例10: 个人CLI工具箱
功能：
1. 自定义快捷命令
2. 常用工具集合
3. 快速调用

运行：
python3 cli_toolkit.py list
python3 cli_toolkit.py run <工具>
"""

import os
import json
import subprocess
from pathlib import Path

# 配置
CONFIG = {
    'data_dir': os.path.expanduser('~/.cli_toolkit'),
}

Path(CONFIG['data_dir']).mkdir(parents=True, exist_ok=True)

TOOLS_FILE = os.path.join(CONFIG['data_dir'], 'tools.json')


class CLIToolkit:
    def __init__(self):
        self.tools = self.load_tools()
    
    def load_tools(self):
        default = {
            'tools': [
                {
                    'name': '天气',
                    'cmd': 'curl wttr.in',
                    'description': '查看天气'
                },
                {
                    'name': 'IP',
                    'cmd': 'curl ifconfig.me',
                    'description': '查看IP地址'
                },
                {
                    'name': '端口',
                    'cmd': 'lsof -i',
                    'description': '查看端口占用'
                },
            ]
        }
        
        if os.path.exists(TOOLS_FILE):
            with open(TOOLS_FILE) as f:
                return json.load(f)
        else:
            self.save_tools(default)
            return default
    
    def save_tools(self, tools):
        with open(TOOLS_FILE, 'w') as f:
            json.dump(tools, f, indent=2, ensure_ascii=False)
    
    def list(self):
        """列出工具"""
        print(f"\n🛠️ CLI工具箱 ({len(self.tools['tools'])}个):")
        
        for tool in self.tools['tools']:
            print(f"  {tool['name']}: {tool['description']}")
    
    def run(self, name):
        """运行工具"""
        for tool in self.tools['tools']:
            if tool['name'] == name:
                print(f"🔄 运行: {tool['name']}")
                os.system(tool['cmd'])
                return
        
        print(f"❌ 未找到工具: {name}")
    
    def add(self, name, cmd, description=''):
        """添加工具"""
        self.tools['tools'].append({
            'name': name,
            'cmd': cmd,
            'description': description
        })
        self.save_tools(self.tools)
        print(f"✅ 已添加工具: {name}")


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""
CLI工具箱 - 使用说明

使用:
  python3 cli_toolkit.py list         # 列表
  python3 cli_toolkit.py run <名称>  # 运行
  python3 cli_toolkit.py add <名称> <命令>  # 添加

示例:
  python3 cli_toolkit.py list
  python3 cli_toolkit.py run 天气
  python3 cli_toolkit.py add hello "echo hello"
""")
        sys.exit(1)
    
    cmd = sys.argv[1]
    toolkit = CLIToolkit()
    
    if cmd == 'list':
        toolkit.list()
    
    elif cmd == 'run' and len(sys.argv) >= 3:
        name = sys.argv[2]
        toolkit.run(name)
    
    elif cmd == 'add' and len(sys.argv) >= 4:
        name = sys.argv[2]
        cmd = sys.argv[3]
        desc = sys.argv[4] if len(sys.argv) > 4 else ''
        toolkit.add(name, cmd, desc)
    
    else:
        print("命令错误")


if __name__ == '__main__':
    main()
