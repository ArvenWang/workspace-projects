#!/usr/bin/env python3
"""
案例68: 会议纪要生成
功能：
1. 原始笔记变正式纪要
2. 提取任务
3. 生成待办

运行：
python3 meeting_notes.py convert <笔记>
"""

import re


class MeetingNotes:
    def __init__(self):
        pass
    
    def convert(self, raw_notes):
        """转换笔记"""
        lines = raw_notes.split('\n')
        
        # 提取信息
        title = lines[0] if lines else "会议纪要"
        content = '\n'.join(lines[1:])
        
        # 提取任务
        tasks = re.findall(r'[-*] (TODO|任务|待办):? (.+)', content)
        
        # 生成格式化纪要
        result = f"""# {title}

## 会议内容
{content}

## 待办事项
"""
        
        for task in tasks:
            result += f"- [ ] {task[1]}\n"
        
        if not tasks:
            result += "无"
        
        return result


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""
会议纪要生成 - 使用说明

使用:
  python3 meeting_notes.py convert <笔记>

示例:
  python3 meeting_notes.py convert "会议讨论了项目进展
  - TODO: 完成API对接
  - TODO: 测试上线"
""")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'convert':
        # 读取 stdin
        import sys
        notes = '\n'.join(sys.stdin.read().split('\n')[1:]) if len(sys.argv) < 3 else ' '.join(sys.argv[2:])
        
        converter = MeetingNotes()
        result = converter.convert(notes)
        print(result)
    else:
        print("命令错误")


if __name__ == '__main__':
    main()
