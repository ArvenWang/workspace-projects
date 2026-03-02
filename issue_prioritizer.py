#!/usr/bin/env python3
"""
案例07: GitHub Issue 排优先级
功能：
1. 按紧急程度排序
2. 分类标签

运行：
python3 issue_prioritizer.py sort <issue列表>
"""

import json


class IssuePrioritizer:
    def __init__(self):
        self.priority_tags = {
            'P0': ['critical', 'urgent', 'blocker'],
            'P1': ['high', 'important', 'bug'],
            'P2': ['medium', 'feature', 'enhancement'],
            'P3': ['low', 'minor', 'nice-to-have']
        }
    
    def prioritize(self, issues):
        """排优先级"""
        results = {'P0': [], 'P1': [], 'P2': [], 'P3': []}
        
        for issue in issues:
            title = issue.get('title', '').lower()
            labels = issue.get('labels', [])
            
            # 匹配优先级
            matched = False
            for priority, tags in self.priority_tags.items():
                for tag in tags:
                    if tag in title or tag in labels:
                        results[priority].append(issue)
                        matched = True
                        break
                if matched:
                    break
            
            if not matched:
                results['P2'].append(issue)
        
        return results
    
    def print_report(self, results):
        """打印报告"""
        print("\n📋 Issue 优先级排序")
        print("="*50)
        
        for priority in ['P0', 'P1', 'P2', 'P3']:
            issues = results[priority]
            if issues:
                print(f"\n🔴 {priority} ({len(issues)}个):")
                for i in issues[:3]:
                    print(f"  - {i.get('title', 'Untitled')}")


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""
Issue排优先级 - 使用说明

使用:
  python3 issue_prioritizer.py sort

示例:
  python3 issue_prioritizer.py sort
""")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'sort':
        # 测试数据
        issues = [
            {'title': 'Critical bug', 'labels': ['bug']},
            {'title': 'New feature', 'labels': ['feature']},
            {'title': 'Fix login', 'labels': ['urgent']},
        ]
        
        prioritizer = IssuePrioritizer()
        results = prioritizer.prioritize(issues)
        prioritizer.print_report(results)
    else:
        print("命令错误")


if __name__ == '__main__':
    main()
