#!/usr/bin/env python3
"""
编程辅助助手 - 完整版
功能：
1. 代码解释
2. Bug修复建议
3. 代码优化
4. 文档生成
5. 代码翻译

依赖：
pip3 install requests

运行：
python3 code_helper.py explain "代码"
python3 code_helper.py optimize "代码"
python3 code_helper.py test "代码"
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime

# 配置
CONFIG = {
    'data_dir': os.path.expanduser('~/.code_helper'),
}

Path(CONFIG['data_dir']).mkdir(parents=True, exist_ok=True)


class CodeHelper:
    def __init__(self):
        self.snippets = self.load_snippets()
    
    def load_snippets(self):
        """加载代码片段库"""
        snippets_file = os.path.join(CONFIG['data_dir'], 'snippets.json')
        
        default = {
            'python': {
                'hello': 'print("Hello, World!")',
                'list': 'my_list = [1, 2, 3]',
                'dict': 'my_dict = {"key": "value"}',
            },
            'javascript': {
                'hello': 'console.log("Hello, World!");',
                'array': 'const arr = [1, 2, 3];',
                'object': 'const obj = {key: "value"};',
            }
        }
        
        if os.path.exists(snippets_file):
            with open(snippets_file) as f:
                return json.load(f)
        else:
            with open(snippets_file, 'w') as f:
                json.dump(default, f, indent=2)
            return default
    
    def save_snippets(self):
        """保存代码片段"""
        snippets_file = os.path.join(CONFIG['data_dir'], 'snippets.json')
        with open(snippets_file, 'w') as f:
            json.dump(self.snippets, f, indent=2)
    
    def detect_language(self, code):
        """检测编程语言"""
        if 'def ' in code or 'import ' in code or 'print(' in code:
            return 'python'
        elif 'function' in code or 'const ' in code or 'let ' in code:
            return 'javascript'
        elif 'public class' in code or 'System.out' in code:
            return 'java'
        elif '<html' in code or '<div' in code:
            return 'html'
        elif 'SELECT ' in code.upper() or 'INSERT ' in code.upper():
            return 'sql'
        return 'unknown'
    
    def explain(self, code):
        """解释代码"""
        lang = self.detect_language(code)
        
        explanations = {
            'python': self.explain_python,
            'javascript': self.explain_js,
        }
        
        if lang in explanations:
            return explanations[lang](code)
        else:
            return f"检测到语言: {lang}\n\n代码片段:\n{code[:200]}"
    
    def explain_python(self, code):
        """解释Python代码"""
        lines = code.split('\n')
        result = ["📖 Python 代码解释:\n"]
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # 导入
            if line.startswith('import '):
                result.append(f"  {i}. 导入模块: {line.replace('import ', '')}")
            elif line.startswith('from '):
                result.append(f"  {i}. 从模块导入: {line}")
            
            # 函数定义
            elif line.startswith('def '):
                name = re.search(r'def (\w+)', line)
                result.append(f"  {i}. 定义函数: {name.group(1) if name else '未知'}")
            
            # 类定义
            elif line.startswith('class '):
                name = re.search(r'class (\w+)', line)
                result.append(f"  {i}. 定义类: {name.group(1) if name else '未知'}")
            
            # 变量赋值
            elif '=' in line and not '==' in line:
                var = line.split('=')[0].strip()
                result.append(f"  {i}. 变量赋值: {var}")
        
        return '\n'.join(result) if len(result) > 1 else "代码分析完成"
    
    def explain_js(self, code):
        """解释JS代码"""
        lines = code.split('\n')
        result = ["📖 JavaScript 代码解释:\n"]
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('//'):
                continue
            
            if 'function' in line:
                name = re.search(r'function (\w+)', line)
                result.append(f"  {i}. 定义函数: {name.group(1) if name else '未知'}")
            elif 'const ' in line or 'let ' in line:
                var = re.search(r'(const|let) (\w+)', line)
                if var:
                    result.append(f"  {i}. 声明变量: {var.group(2)}")
        
        return '\n'.join(result) if len(result) > 1 else "代码分析完成"
    
    def optimize(self, code):
        """优化建议"""
        lang = self.detect_language(code)
        result = [f"🔧 {lang} 代码优化建议:\n"]
        
        # 简单检查
        if len(code) > 500:
            result.append("  • 代码较长，建议拆分函数")
        
        if 'for' in code and 'range' in code:
            result.append("  • 考虑使用列表推导式")
        
        if code.count('if') > 5:
            result.append("  • 条件过多，考虑使用字典映射")
        
        if '==' in code:
            result.append("  • 比较操作注意使用 is == 替代")
        
        if not result[1:]:
            result.append("  • 代码看起来不错！")
        
        return '\n'.join(result)
    
    def generate_tests(self, code):
        """生成测试"""
        lang = self.detect_language(code)
        
        if lang == 'python':
            # 提取函数名
            func_match = re.search(r'def (\w+)', code)
            func_name = func_match.group(1) if func_match else 'function'
            
            test_code = f'''import unittest

class Test{func_name.capitalize()}(unittest.TestCase):
    def test_basic(self):
        # TODO: 添加测试
        pass

if __name__ == "__main__":
    unittest.main()
'''
            return test_code
        
        return "# 请手动编写测试"
    
    def generate_docs(self, code):
        """生成文档"""
        lang = self.detect_language(code)
        
        if lang == 'python':
            # 提取函数
            func_match = re.search(r'def (\w+)\((.*?)\):', code)
            if func_match:
                name = func_match.group(1)
                params = func_match.group(2)
                
                doc = f'''## {name}

### 参数
{params or "无"}

### 返回值
无

### 示例
```python
{code}
```

### 说明
TODO: 添加说明
'''
                return doc
        
        return "无法生成文档"


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""
编程辅助助手 - 使用说明

使用:
  python3 code_helper.py explain <代码>    # 解释代码
  python3 code_helper.py optimize <代码>  # 优化建议
  python3 code_helper.py test <代码>      # 生成测试
  python3 code_helper.py docs <代码>      # 生成文档
  python3 code_helper.py snippet <语言>  # 代码片段

示例:
  python3 code_helper.py explain "def hello(): print('hi')"
  python3 code_helper.py snippet python
""")
        sys.exit(1)
    
    cmd = sys.argv[1]
    helper = CodeHelper()
    
    if cmd == 'explain' and len(sys.argv) >= 3:
        code = ' '.join(sys.argv[2:])
        print(helper.explain(code))
    
    elif cmd == 'optimize' and len(sys.argv) >= 3:
        code = ' '.join(sys.argv[2:])
        print(helper.optimize(code))
    
    elif cmd == 'test' and len(sys.argv) >= 3:
        code = ' '.join(sys.argv[2:])
        print(helper.generate_tests(code))
    
    elif cmd == 'docs' and len(sys.argv) >= 3:
        code = ' '.join(sys.argv[2:])
        print(helper.generate_docs(code))
    
    elif cmd == 'snippet' and len(sys.argv) >= 3:
        lang = sys.argv[2]
        snippets = helper.snippets.get(lang, {})
        print(f"\n📝 {lang} 代码片段:")
        for name, code in snippets.items():
            print(f"\n{name}:")
            print(f"  {code}")
    
    else:
        print("命令错误")


if __name__ == '__main__':
    main()
