#!/usr/bin/env python3
"""
案例10: CLI工具箱(完整版)
"""

class CLIToolkitComplete:
    def __init__(self):
        self.tools = {}
    
    def register(self, name, cmd, desc=''):
        self.tools[name] = {'cmd': cmd, 'desc': desc}
        print(f"✅ 注册工具: {name}")
    
    def run(self, name):
        if name in self.tools:
            print(f"🔧 运行: {name}")
            import os
            os.system(self.tools[name]['cmd'])
        else:
            print(f"❌ 工具不存在: {name}")
    
    def list(self):
        print("\n🛠️ 工具箱:")
        for name, tool in self.tools.items():
            desc = tool['desc'] or ''
            print(f"  {name}: {desc}")


if __name__ == '__main__':
    toolkit = CLIToolkitComplete()
    toolkit.register('天气', 'curl wttr.in', '查看天气')
    toolkit.register('IP', 'curl ifconfig.me', '查看IP')
    toolkit.list()
