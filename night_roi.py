#!/usr/bin/env python3
"""
案例48: 夜间ROI追踪
功能：
1. 追踪夜间工作效果
2. ROI计算
"""

class NightROI:
    def __init__(self):
        self.tasks = []
    
    def add(self, task, hours, value):
        self.tasks.append({
            'task': task,
            'hours': hours,
            'value': value,
            'roi': value / hours if hours > 0 else 0
        })
    
    def report(self):
        print("\n📈 夜间ROI报告")
        print("="*50)
        
        total_hours = sum(t['hours'] for t in self.tasks)
        total_value = sum(t['value'] for t in self.tasks)
        
        print(f"  总工时: {total_hours}h")
        print(f"  总价值: ${total_value}")
        print(f"  平均ROI: ${total_value/total_hours:.2f}/h" if total_hours else "  N/A")


if __name__ == '__main__':
    roi = NightROI()
    roi.add('案例开发', 2, 100)
    roi.add('代码优化', 1, 50)
    roi.report()
