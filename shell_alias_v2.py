#!/usr/bin/env python3
"""
案例05: Shell别名构建器(完整版)
"""

class ShellAliasBuilder:
    def __init__(self):
        self.aliases = {}
        self.history = []
    
    def learn(self, command):
        """学习常用命令"""
        self.history.append(command)
        print(f"📝 记录: {command}")
    
    def suggest(self):
        """建议别名"""
        from collections import Counter
        cmds = Counter(self.history)
        
        print("\n💡 别名建议:")
        suggestions = [
            ('g', 'git'),
            ('gc', 'git commit'),
            ('ll', 'ls -la'),
        ]
        
        for alias, cmd in suggestions:
            print(f"  alias {alias}='{cmd}'")


if __name__ == '__main__':
    builder = ShellAliasBuilder()
    builder.learn('git commit -m "fix"')
    builder.learn('git push')
    builder.learn('git status')
    builder.suggest()
