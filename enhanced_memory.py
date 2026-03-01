#!/usr/bin/env python3
"""
增强记忆系统 - 基于 workspace 文件结构
功能：
1. 自动沉淀 - 从每日日志提取关键信息
2. 关键词检索 - 搜索历史记忆
3. 对齐检查 - 确保记忆一致性

运行：
python3 enhanced_memory.py沉积   # 从每日日志沉淀到长期记忆
python3 enhanced_memory.py 搜索 <关键词>   # 搜索记忆
python3 enhanced_memory.py 状态   # 查看记忆状态
"""

import os
import re
import json
from datetime import datetime, timedelta
from pathlib import Path

# 配置
WORKSPACE = os.path.expanduser('~/.openclaw/workspace')
MEMORY_DIR = os.path.join(WORKSPACE, 'memory')
LONG_TERM_FILE = os.path.join(WORKSPACE, 'MEMORY.md')
ALIGN_FILE = os.path.join(WORKSPACE, '.memory_alignment.json')


class EnhancedMemory:
    """增强记忆系统"""
    
    def __init__(self):
        self.workspace = WORKSPACE
        self.memory_dir = MEMORY_DIR
        self.long_term_file = LONG_TERM_FILE
        self.alignment_file = ALIGN_FILE
        self.alignment = self.load_alignment()
        
    def load_alignment(self):
        """加载对齐状态"""
        if os.path.exists(self.alignment_file):
            with open(self.alignment_file) as f:
                return json.load(f)
        return {
            'last_consolidation': None,
            'consolidated_days': [],
            'last_search': None
        }
    
    def save_alignment(self):
        """保存对齐状态"""
        with open(self.alignment_file, 'w') as f:
            json.dump(self.alignment, f, indent=2)
    
    def get_recent_logs(self, days=7):
        """获取最近日志"""
        if not os.path.exists(self.memory_dir):
            return []
        
        files = []
        for f in os.listdir(self.memory_dir):
            if f.endswith('.md') and f != 'README.md':
                files.append(f)
        
        files.sort(reverse=True)
        return files[:days]
    
    def extract_key_info(self, content):
        """从日志中提取关键信息"""
        key_info = []
        
        # 提取任务完成情况
        task_pattern = r'[✅❌🔴].*'
        tasks = re.findall(task_pattern, content)
        key_info.extend(tasks[:5])  # 最多5条
        
        # 提取决策类内容
        decision_pattern = r'.*决定.*|.*规划.*|.*目标.*'
        decisions = re.findall(decision_pattern, content)
        key_info.extend(decisions[:3])
        
        return key_info
    
    def consolidate(self):
        """沉淀：将近期日志关键信息存入长期记忆"""
        print("🔄 开始沉淀...")
        
        # 读取现有长期记忆
        long_term_content = ""
        if os.path.exists(self.long_term_file):
            with open(self.long_term_file) as f:
                long_term_content = f.read()
        
        # 获取未沉淀的日志
        consolidated = set(self.alignment.get('consolidated_days', []))
        recent_logs = self.get_recent_logs(days=7)
        
        new_info = []
        for log_file in recent_logs:
            day = log_file.replace('.md', '')
            if day in consolidated:
                continue
            
            log_path = os.path.join(self.memory_dir, log_file)
            with open(log_path) as f:
                content = f.read()
            
            key_info = self.extract_key_info(content)
            if key_info:
                new_info.append(f"\n### {day}\n")
                new_info.extend([f"- {info}" for info in key_info])
        
        if not new_info:
            print("✅ 无新信息需要沉淀")
            return
        
        # 追加到长期记忆
        with open(self.long_term_file, 'a') as f:
            f.write("\n\n## 最近沉淀\n")
            f.write('\n'.join(new_info))
        
        # 更新对齐状态
        self.alignment['consolidated_days'].extend(
            [log_file.replace('.md', '') for log_file in recent_logs]
        )
        self.alignment['last_consolidation'] = datetime.now().isoformat()
        self.save_alignment()
        
        print(f"✅ 已沉淀 {len(new_info)} 条信息")
    
    def search(self, keyword):
        """搜索记忆"""
        print(f"🔍 搜索: {keyword}")
        results = []
        
        # 搜索每日日志
        if os.path.exists(self.memory_dir):
            for f in os.listdir(self.memory_dir):
                if not f.endswith('.md'):
                    continue
                path = os.path.join(self.memory_dir, f)
                with open(path) as file:
                    content = file.read()
                    if keyword.lower() in content.lower():
                        # 找到包含关键词的行
                        lines = content.split('\n')
                        matches = [l for l in lines if keyword.lower() in l.lower()]
                        results.append((f, matches[:3]))
        
        # 搜索长期记忆
        if os.path.exists(self.long_term_file):
            with open(self.long_term_file) as f:
                content = f.read()
                if keyword.lower() in content.lower():
                    lines = content.split('\n')
                    matches = [l for l in lines if keyword.lower() in l.lower()]
                    results.append(('MEMORY.md', matches[:3]))
        
        # 显示结果
        if not results:
            print("未找到相关内容")
            return
        
        for source, matches in results:
            print(f"\n📁 {source}")
            for m in matches:
                print(f"  {m}")
        
        self.alignment['last_search'] = datetime.now().isoformat()
        self.save_alignment()
    
    def status(self):
        """查看状态"""
        print("📊 记忆状态\n")
        
        # 长期记忆
        if os.path.exists(self.long_term_file):
            with open(self.long_term_file) as f:
                lines = len(f.readlines())
            print(f"长期记忆: {lines} 行")
        
        # 每日日志
        if os.path.exists(self.memory_dir):
            files = [f for f in os.listdir(self.memory_dir) if f.endswith('.md')]
            print(f"每日日志: {len(files)} 个")
        
        # 对齐状态
        print(f"上次沉淀: {self.alignment.get('last_consolidation', '从未')}")
        print(f"已沉淀天数: {len(self.alignment.get('consolidated_days', []))}")


if __name__ == '__main__':
    import sys
    
    memory = EnhancedMemory()
    
    if len(sys.argv) < 2:
        memory.status()
    elif sys.argv[1] == '沉淀':
        memory.consolidate()
    elif sys.argv[1] == '搜索' and len(sys.argv) > 2:
        memory.search(sys.argv[2])
    elif sys.argv[1] == '状态':
        memory.status()
    else:
        print(__doc__)
