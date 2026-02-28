#!/usr/bin/env python3
"""
案例19: 日志异常检测
功能：
1. 检测错误日志
2. 统计异常
3. 告警

运行：
python3 log_analyzer.py analyze <日志文件>
"""

import re
from collections import Counter


class LogAnalyzer:
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def analyze(self, log_content):
        """分析日志"""
        lines = log_content.split('\n')
        
        error_pattern = re.compile(r'(ERROR|FATAL|CRITICAL)', re.I)
        warning_pattern = re.compile(r'(WARN|WARNING)', re.I)
        
        for i, line in enumerate(lines, 1):
            if error_pattern.search(line):
                self.errors.append({'line': i, 'content': line})
            elif warning_pattern.search(line):
                self.warnings.append({'line': i, 'content': line})
        
        return {
            'errors': len(self.errors),
            'warnings': len(self.warnings),
            'total': len(lines)
        }
    
    def report(self):
        """生成报告"""
        print(f"\n📊 日志分析报告")
        print("="*50)
        print(f"  错误: {len(self.errors)}个")
        print(f"  警告: {len(self.warnings)}个")
        
        if self.errors:
            print(f"\n❌ 错误详情:")
            for e in self.errors[:5]:
                print(f"  Line {e['line']}: {e['content'][:60]}")


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""
日志分析器 - 使用说明

使用:
  python3 log_analyzer.py analyze <日志内容>

示例:
  python3 log_analyzer.py analyze "ERROR: 连接失败\nWARNING: 超时"
""")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'analyze' and len(sys.argv) >= 3:
        content = ' '.join(sys.argv[2:])
        analyzer = LogAnalyzer()
        result = analyzer.analyze(content)
        analyzer.report()
    else:
        print("命令错误")


if __name__ == '__main__':
    main()
