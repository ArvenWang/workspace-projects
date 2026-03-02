#!/usr/bin/env python3
"""
案例40: 知识图谱重建
功能：
1. 夜间重建知识图谱
2. 关联分析
"""

import json
from datetime import datetime


class KnowledgeGraphRebuilder:
    def __init__(self):
        self.entities = []
    
    def add_entity(self, name, type, relations=None):
        """添加实体"""
        entity = {
            'name': name,
            'type': type,
            'relations': relations or [],
            'added': datetime.now().isoformat()
        }
        self.entities.append(entity)
    
    def build(self):
        """构建图谱"""
        print("\n🔄 重建知识图谱...")
        
        # 分析关联
        connections = {}
        
        for e in self.entities:
            for rel in e.get('relations', []):
                key = f"{e['name']}->{rel}"
                connections[key] = connections.get(key, 0) + 1
        
        print(f"  实体: {len(self.entities)}个")
        print(f"  关联: {len(connections)}个")
        
        return connections
    
    def stats(self):
        """统计"""
        print("\n📊 知识图谱统计")
        print("="*40)
        print(f"  总实体: {len(self.entities)}")
        
        by_type = {}
        for e in self.entities:
            t = e['type']
            by_type[t] = by_type.get(t, 0) + 1
        
        print(f"  类型分布:")
        for t, c in by_type.items():
            print(f"    {t}: {c}")


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("使用: python3 knowledge_graph.py build")
        sys.exit(1)
    
    cmd = sys.argv[1]
    kg = KnowledgeGraphRebuilder()
    
    # 测试数据
    kg.add_entity('Python', '语言', ['编程', 'AI'])
    kg.add_entity('AI', '领域', ['Python', '机器学习'])
    
    if cmd == 'build':
        kg.build()
    elif cmd == 'stats':
        kg.stats()


if __name__ == '__main__':
    main()
