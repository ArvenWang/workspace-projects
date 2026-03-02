#!/usr/bin/env python3
"""
案例05: 夜间Shell别名构建器
功能：
1. 分析命令使用习惯
2. 自动创建快捷命令
3. 学习常用工作流

运行：
python3 shell_alias_builder.py analyze
python3 shell_alias_builder.py add <别名> <命令>
python3 shell_alias_builder.py list
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from collections import Counter

# 配置
CONFIG = {
    'data_dir': os.path.expanduser('~/.shell_alias_builder'),
    'history_file': os.path.expanduser('~/.zsh_history'),
    'alias_file': os.path.expanduser('~/.zsh_aliases'),
}

Path(CONFIG['data_dir']).mkdir(parents=True, exist_ok=True)

ALIASES_FILE = os.path.join(CONFIG['data_dir'], 'aliases.json')
PATTERNS_FILE = os.path.join(CONFIG['data_dir'], 'patterns.json')


class ShellAliasBuilder:
    def __init__(self):
        self.aliases = self.load_aliases()
        self.patterns = self.load_patterns()
    
    def load_aliases(self):
        if os.path.exists(ALIASES_FILE):
            with open(ALIASES_FILE) as f:
                return json.load(f)
        return {}
    
    def save_aliases(self):
        with open(ALIASES_FILE, 'w') as f:
            json.dump(self.aliases, f, indent=2, ensure_ascii=False)
    
    def load_patterns(self):
        if os.path.exists(PATTERNS_FILE):
            with open(PATTERNS_FILE) as f:
                return json.load(f)
        return {'commands': [], 'sequences': []}
    
    def save_patterns(self):
        with open(PATTERNS_FILE, 'w') as f:
            json.dump(self.patterns, f, indent=2)
    
    def analyze_history(self):
        """分析历史命令"""
        print(f"\n🔍 分析命令历史...")
        
        history_file = CONFIG['history_file']
        if not os.path.exists(history_file):
            print(f"❌ 未找到历史文件: {history_file}")
            return
        
        commands = []
        
        with open(history_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                # 提取命令
                line = line.strip()
                if line:
                    # 去掉时间戳
                    if ':' in line.split()[0] if line.split() else False:
                        parts = line.split(';', 1)
                        if len(parts) > 1:
                            cmd = parts[1].strip()
                            if cmd:
                                commands.append(cmd)
        
        # 统计高频命令
        cmd_counts = Counter(commands)
        
        print(f"\n📊 最常用命令 Top 20:")
        for cmd, count in cmd_counts.most_common(20):
            print(f"  {count:4d}x  {cmd[:60]}")
        
        # 提取常用序列
        self.find_sequences(commands)
        
        return cmd_counts
    
    def find_sequences(self, commands):
        """找常用命令序列"""
        sequences = []
        
        # 找连续使用的命令
        for i in range(len(commands) - 1):
            seq = f"{commands[i]} && {commands[i+1]}"
            sequences.append(seq)
        
        seq_counts = Counter(sequences)
        
        print(f"\n🔗 常用命令序列:")
        for seq, count in seq_counts.most_common(5):
            if count > 1:
                print(f"  {count}x  {seq[:50]}")
        
        self.patterns['sequences'] = [
            {'seq': s, 'count': c} 
            for s, c in seq_counts.most_common(10) if c > 1
        ]
        self.save_patterns()
    
    def add_alias(self, alias, command):
        """添加别名"""
        self.aliases[alias] = {
            'command': command,
            'created_at': datetime.now().isoformat(),
            'usage_count': 0
        }
        self.save_aliases()
        print(f"✅ 已添加别名: {alias} -> {command}")
        
        # 写入.zsh_aliases
        self.write_to_shell()
    
    def write_to_shell(self):
        """写入shell配置"""
        lines = ["# Aliases added by AI"]
        for alias, info in self.aliases.items():
            lines.append(f"alias {alias}='{info['command']}'")
        
        with open(CONFIG['alias_file'], 'w') as f:
            f.write('\n'.join(lines))
        
        print(f"✅ 已写入: {CONFIG['alias_file']}")
        print(f"   运行: source {CONFIG['alias_file']}")
    
    def list_aliases(self):
        """列出所有别名"""
        if not self.aliases:
            print("📝 暂无别名")
            return
        
        print(f"\n📋 别名列表 ({len(self.aliases)}个):")
        for alias, info in self.aliases.items():
            print(f"  {alias} -> {info['command']}")
    
    def suggest_aliases(self):
        """建议别名"""
        print(f"\n💡 别名建议:")
        
        suggestions = [
            ('ll', 'ls -la'),
            ('la', 'ls -A'),
            ('l', 'ls -CF'),
            ('grep', 'grep --color=auto'),
            ('..', 'cd ..'),
            ('...', 'cd ../..'),
        ]
        
        for alias, cmd in suggestions:
            if alias not in self.aliases:
                print(f"  {alias} -> {cmd}")
        
        # 从分析结果建议
        if self.patterns.get('sequences'):
            print(f"\n从命令序列建议:")
            for p in self.patterns['sequences'][:3]:
                seq = p['seq']
                if '&&' in seq:
                    parts = seq.split(' && ')
                    if len(parts) == 2:
                        # 简单建议
                        pass


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""
Shell别名构建器 - 使用说明

使用:
  python3 shell_alias_builder.py analyze   # 分析历史
  python3 shell_alias_builder.py add <别名> <命令>  # 添加
  python3 shell_alias_builder.py list     # 列表
  python3 shell_alias_builder.py suggest  # 建议

示例:
  python3 shell_alias_builder.py analyze
  python3 shell_alias_builder.py add g git
  python3 shell_alias_builder.py list
""")
        sys.exit(1)
    
    cmd = sys.argv[1]
    builder = ShellAliasBuilder()
    
    if cmd == 'analyze':
        builder.analyze_history()
    
    elif cmd == 'add' and len(sys.argv) >= 4:
        alias = sys.argv[2]
        command = sys.argv[3]
        builder.add_alias(alias, command)
    
    elif cmd == 'list':
        builder.list_aliases()
    
    elif cmd == 'suggest':
        builder.suggest_aliases()
    
    else:
        print("命令错误")


if __name__ == '__main__':
    main()
