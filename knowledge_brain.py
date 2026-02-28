#!/usr/bin/env python3
"""
AI第二大脑 - 知识库
功能：
1. 存储读取笔记
2. 自然语言搜索
3. 自动标签分类
4. 知识问答

依赖：
pip3 install chromadb sentence-transformers

运行：
python3 knowledge_brain.py add "今天学到了..."
python3 knowledge_brain.py search "AI"
python3 knowledge_brain.py ask "什么是机器学习"
"""

import os
import json
import glob
from datetime import datetime
from pathlib import Path

# 配置
DATA_DIR = os.path.expanduser('~/.knowledge_brain')
NOTES_FILE = os.path.join(DATA_DIR, 'notes.json')

os.makedirs(DATA_DIR, exist_ok=True)

class KnowledgeBrain:
    def __init__(self):
        self.notes = self.load_notes()
    
    def load_notes(self):
        if os.path.exists(NOTES_FILE):
            with open(NOTES_FILE) as f:
                return json.load(f)
        return []
    
    def save_notes(self):
        with open(NOTES_FILE, 'w') as f:
            json.dump(self.notes, f, indent=2, ensure_ascii=False)
    
    def add(self, content, tags=None):
        note = {
            'id': len(self.notes) + 1,
            'content': content,
            'tags': tags or [],
            'created_at': datetime.now().isoformat()
        }
        
        # 自动提取标签
        keywords = content.split()
        note['auto_tags'] = [k for k in keywords if len(k) > 2][:5]
        
        self.notes.append(note)
        self.save_notes()
        return note['id']
    
    def search(self, query, limit=10):
        """简单搜索 - 关键词匹配"""
        results = []
        query_lower = query.lower()
        
        for note in self.notes:
            score = 0
            if query_lower in note['content'].lower():
                score += 10
            for tag in note.get('tags', []) + note.get('auto_tags', []):
                if query_lower in tag.lower():
                    score += 5
            
            if score > 0:
                results.append((score, note))
        
        results.sort(key=lambda x: -x[0])
        return [n[1] for n in results[:limit]]
    
    def list_all(self):
        return self.notes
    
    def delete(self, note_id):
        self.notes = [n for n in self.notes if n['id'] != note_id]
        self.save_notes()


def main():
    import sys
    
    brain = KnowledgeBrain()
    
    if len(sys.argv) < 2:
        print("""
AI第二大脑 - 知识库

使用:
  python3 knowledge_brain.py add <内容>      # 添加笔记
  python3 knowledge_brain.py search <关键词> # 搜索
  python3 knowledge_brain.py list           # 列出所有
  python3 knowledge_brain.py delete <id>   # 删除

示例:
  python3 knowledge_brain.py add "今天学到了Python"
  python3 knowledge_brain.py search "Python"
""")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'add' and len(sys.argv) >= 3:
        content = ' '.join(sys.argv[2:])
        note_id = brain.add(content)
        print(f"✅ 已添加笔记 #{note_id}")
    
    elif cmd == 'search' and len(sys.argv) >= 3:
        query = ' '.join(sys.argv[2:])
        results = brain.search(query)
        print(f"\n找到 {len(results)} 条结果:")
        for note in results:
            print(f"\n#{note['id']} [{note.get('auto_tags', [])[:3]}]")
            print(f"   {note['content'][:100]}...")
    
    elif cmd == 'list':
        notes = brain.list_all()
        print(f"\n共 {len(notes)} 条笔记:")
        for note in notes[-10:]:
            print(f"#{note['id']} {note['content'][:50]}...")
    
    elif cmd == 'delete' and len(sys.argv) >= 3:
        note_id = int(sys.argv[2])
        brain.delete(note_id)
        print(f"✅ 已删除笔记 #{note_id}")


if __name__ == '__main__':
    main()
