#!/usr/bin/env python3
"""
案例27: Token使用优化
功能：
1. 统计Token使用
2. 优化建议

运行：
python3 token_optimizer.py stats
"""

import json
from datetime import datetime


class TokenOptimizer:
    def __init__(self):
        self.usage = []
    
    def add(self, model, input_tokens, output_tokens):
        """添加使用记录"""
        entry = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'model': model,
            'input': input_tokens,
            'output': output_tokens,
            'total': input_tokens + output_tokens
        }
        self.usage.append(entry)
    
    def stats(self):
        """统计"""
        if not self.usage:
            print("暂无数据")
            return
        
        total = sum(u['total'] for u in self.usage)
        by_model = {}
        
        for u in self.usage:
            model = u['model']
            if model not in by_model:
                by_model[model] = {'count': 0, 'tokens': 0}
            by_model[model]['count'] += 1
            by_model[model]['tokens'] += u['total']
        
        print(f"\n📊 Token使用统计")
        print("="*50)
        print(f"  总请求: {len(self.usage)}次")
        print(f"  总Token: {total:,}")
        
        print(f"\n按模型:")
        for model, data in by_model.items():
            print(f"  {model}: {data['tokens']:,} tokens ({data['count']}次)")
        
        # 优化建议
        print(f"\n💡 优化建议:")
        print(f"  - 考虑使用更小的模型处理简单任务")
        print(f"  - 缓存重复请求")


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""
Token优化器 - 使用说明

使用:
  python3 token_optimizer.py stats
  python3 token_optimizer.py add <模型> <输入> <输出>

示例:
  python3 token_optimizer.py stats
  python3 token_optimizer.py add gpt-4 1000 500
""")
        sys.exit(1)
    
    cmd = sys.argv[1]
    optimizer = TokenOptimizer()
    
    if cmd == 'stats':
        optimizer.stats()
    
    elif cmd == 'add' and len(sys.argv) >= 5:
        model = sys.argv[2]
        input_t = int(sys.argv[3])
        output_t = int(sys.argv[4])
        optimizer.add(model, input_t, output_t)
        print("✅ 已添加")
        optimizer.stats()
    
    else:
        print("命令错误")


if __name__ == '__main__':
    main()
