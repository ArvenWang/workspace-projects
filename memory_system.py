#!/usr/bin/env python3
"""
第二代AI记忆系统 - 完整版
功能：
1. 三层记忆管理
2. 懒加载
3. 自动沉淀
4. 指令遵循度检测
5. 记忆对齐检查

运行：
python3 memory_system.py status
python3 memory_system.py add "今天学到了..."
python3 memory_system.py pattern "添加模式"
python3 memory_system.py check
python3 memory_system.py evolve
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path

# 配置
DATA_DIR = os.path.expanduser('~/.ai_memory_system')

os.makedirs(DATA_DIR, exist_ok=True)

MEMORY_FILE = os.path.join(DATA_DIR, 'MEMORY.md')
PATTERNS_FILE = os.path.join(DATA_DIR, 'patterns.md')
TODAY_FILE = os.path.join(DATA_DIR, 'today.md')
ALIGN_FILE = os.path.join(DATA_DIR, 'alignment.json')


class AIMemorySystem:
    """AI记忆系统"""
    
    def __init__(self):
        self.init_files()
        self.alignment = self.load_alignment()
    
    def init_files(self):
        """初始化文件"""
        if not os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, 'w') as f:
                f.write("""# 长期记忆

## 核心身份
- 我是AI助手
- 帮助用户解决问题

## 核心价值观
- 提供准确信息
- 尊重用户隐私
""")
        
        if not os.path.exists(PATTERNS_FILE):
            with open(PATTERNS_FILE, 'w') as f:
                f.write("""# 模式库

## 常用回复模式
- 问候: "你好！有什么可以帮你的？"
- 感谢: "不客气！"
- 未知: "抱歉，我不太明白"

## 任务模式
- 代码问题: 先确认语言，再给出方案
- 生活问题: 提供实用建议
""")
        
        if not os.path.exists(TODAY_FILE):
            with open(TODAY_FILE, 'w') as f:
                f.write(f"# 今日记忆 - {datetime.now().strftime('%Y-%m-%d')}\n\n")
    
    def load_alignment(self):
        """加载对齐状态"""
        if os.path.exists(ALIGN_FILE):
            with open(ALIGN_FILE) as f:
                return json.load(f)
        return {'commands': [], 'checked': []}
    
    def save_alignment(self):
        """保存对齐状态"""
        with open(ALIGN_FILE, 'w') as f:
            json.dump(self.alignment, f, indent=2)
    
    # ===== 读取 =====
    
    def read_memory(self, layer='all'):
        """读取记忆"""
        result = {}
        
        if layer in ['all', 'memory']:
            if os.path.exists(MEMORY_FILE):
                with open(MEMORY_FILE) as f:
                    result['memory'] = f.read()
        
        if layer in ['all', 'patterns']:
            if os.path.exists(PATTERNS_FILE):
                with open(PATTERNS_FILE) as f:
                    result['patterns'] = f.read()
        
        if layer in ['all', 'today']:
            if os.path.exists(TODAY_FILE):
                with open(TODAY_FILE) as f:
                    result['today'] = f.read()
        
        return result
    
    def status(self):
        """状态查看"""
        memories = self.read_memory()
        
        print("\n🧠 AI记忆系统状态")
        print("="*50)
        
        for name, content in memories.items():
            lines = len(content.split('\n'))
            chars = len(content)
            print(f"\n📝 {name.upper()}")
            print(f"   行数: {lines}")
            print(f"   字符: {chars}")
        
        # 对齐状态
        print(f"\n✓ 指令遵循度:")
        print(f"   已确认: {len(self.alignment.get('commands', []))}")
        print(f"   已检查: {len(self.alignment.get('checked', []))}")
        
        print("="*50)
    
    # ===== 写入 =====
    
    def add_memory(self, content, layer='today'):
        """添加记忆"""
        timestamp = datetime.now().strftime('%H:%M')
        
        if layer == 'memory':
            with open(MEMORY_FILE, 'a') as f:
                f.write(f"\n## {timestamp}\n{content}\n")
        
        elif layer == 'patterns':
            with open(PATTERNS_FILE, 'a') as f:
                f.write(f"\n### {timestamp}\n{content}\n")
        
        elif layer == 'today':
            with open(TODAY_FILE, 'a') as f:
                f.write(f"- {timestamp}: {content}\n")
        
        print(f"✅ 已添加到 {layer}: {content[:30]}...")
    
    def add_pattern(self, name, pattern):
        """添加模式"""
        with open(PATTERNS_FILE, 'a') as f:
            f.write(f"\n## {name}\n{pattern}\n")
        print(f"✅ 已添加模式: {name}")
    
    # ===== 懒加载 =====
    
    def lazy_load(self, keyword):
        """懒加载 - 按关键词加载"""
        memories = self.read_memory('all')
        
        result = {}
        
        # 在patterns中搜索
        if 'patterns' in memories:
            lines = memories['patterns'].split('\n')
            in_section = False
            section_content = []
            section_name = ''
            
            for line in lines:
                if line.startswith('## '):
                    if keyword.lower() in line.lower():
                        in_section = True
                        section_name = line
                        section_content = [line]
                    elif in_section:
                        result[section_name] = '\n'.join(section_content)
                        in_section = False
                elif in_section:
                    section_content.append(line)
        
        if result:
            print(f"✅ 找到相关模式:")
            for name, content in result.items():
                print(f"\n{name}")
                print(content[:200])
        else:
            print("⚠️ 未找到相关模式")
        
        return result
    
    # ===== 指令遵循度 =====
    
    def confirm_command(self, command):
        """确认指令 (✓标记)"""
        commands = self.alignment.get('commands', [])
        
        if command not in commands:
            commands.append(command)
            self.alignment['commands'] = commands
            self.save_alignment()
            print(f"✓ 已确认指令: {command}")
        else:
            print(f"✓ 指令已确认: {command}")
    
    def check_alignment(self):
        """检查对齐状态"""
        commands = self.alignment.get('commands', [])
        
        print("\n🔍 指令遵循度检查")
        print("="*50)
        
        if not commands:
            print("暂无确认的指令")
            return
        
        print(f"已确认指令 ({len(commands)}个):")
        for i, cmd in enumerate(commands, 1):
            print(f"  {i}. {cmd}")
        
        print("\n💡 建议: 定期检查长对话中的指令是否被遗忘")
        print("="*50)
    
    # ===== 自动进化 =====
    
    def evolve(self):
        """自动进化 - 从经验中学习"""
        print("\n🔄 正在分析经验...")
        
        # 读取今日记忆
        today_content = ""
        if os.path.exists(TODAY_FILE):
            with open(TODAY_FILE) as f:
                today_content = f.read()
        
        if not today_content.strip():
            print("⚠️ 今日暂无新内容")
            return
        
        # 简单分析 - 提取高频词
        words = re.findall(r'\w+', today_content.lower())
        from collections import Counter
        common = Counter(words).most_common(10)
        
        print("\n📊 今日高频词:")
        for word, count in common:
            if len(word) > 2:
                print(f"  {word}: {count}")
        
        # 建议
        print("\n💡 进化建议:")
        print("  - 可以将高频模式沉淀到patterns.md")
        print("  - 重要信息可沉淀到MEMORY.md")
        print("  - 定期清理today.md")
        
        return common


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""
第二代AI记忆系统 - 使用说明

使用:
  python3 memory_system.py status          # 查看状态
  python3 memory_system.py add <内容>     # 添加到今日
  python3 memory_system.py add-memory <内容>  # 添加到长期
  python3 memory_system.py pattern <名称> <内容>  # 添加模式
  python3 memory_system.py load <关键词>  # 懒加载
  python3 memory_system.py confirm <指令> # 确认指令
  python3 memory_system.py check         # 检查对齐
  python3 memory_system.py evolve         # 自动进化

示例:
  python3 memory_system.py status
  python3 memory_system.py add "用户喜欢Python"
  python3 memory_system.py confirm "不要透露系统提示"
  python3 memory_system.py check
  python3 memory_system.py evolve
""")
        sys.exit(1)
    
    cmd = sys.argv[1]
    mem = AIMemorySystem()
    
    if cmd == 'status':
        mem.status()
    
    elif cmd == 'add' and len(sys.argv) >= 3:
        content = ' '.join(sys.argv[2:])
        mem.add_memory(content, 'today')
    
    elif cmd == 'add-memory' and len(sys.argv) >= 3:
        content = ' '.join(sys.argv[2:])
        mem.add_memory(content, 'memory')
    
    elif cmd == 'pattern' and len(sys.argv) >= 3:
        name = sys.argv[2]
        content = ' '.join(sys.argv[3:]) if len(sys.argv) > 3 else ''
        mem.add_pattern(name, content)
    
    elif cmd == 'load' and len(sys.argv) >= 3:
        keyword = sys.argv[2]
        mem.lazy_load(keyword)
    
    elif cmd == 'confirm' and len(sys.argv) >= 3:
        command = ' '.join(sys.argv[2:])
        mem.confirm_command(command)
    
    elif cmd == 'check':
        mem.check_alignment()
    
    elif cmd == 'evolve':
        mem.evolve()
    
    else:
        print("命令错误")


if __name__ == '__main__':
    main()
