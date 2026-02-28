#!/usr/bin/env python3
"""
案例21: 邮件自动分类
功能：
1. 按紧急程度分类
2. 自动打标签

运行：
python3 email_classifier.py classify <邮件内容>
"""

import re


class EmailClassifier:
    def __init__(self):
        self.categories = {
            '紧急': ['紧急', '立刻', '马上', 'ASAP', 'urgent'],
            '重要': ['重要', '关键', '必须', 'important'],
            '待办': ['需要', '请', '麻烦', 'todo'],
            '参考': ['转发', 'FYI', '参考']
        }
    
    def classify(self, content):
        """分类"""
        content_lower = content.lower()
        
        for category, keywords in self.categories.items():
            for kw in keywords:
                if kw.lower() in content_lower:
                    return category
        
        return '普通'
    
    def extract_sender(self, content):
        """提取发件人"""
        match = re.search(r'From: (.+)', content)
        return match.group(1) if match else '未知'
    
    def extract_subject(self, content):
        """提取主题"""
        match = re.search(r'Subject: (.+)', content)
        return match.group(1) if match else '无主题'


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""
邮件分类器 - 使用说明

使用:
  python3 email_classifier.py classify <内容>

示例:
  python3 email_classifier.py classify "紧急：请立即处理"
""")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'classify' and len(sys.argv) >= 3:
        content = ' '.join(sys.argv[2:])
        classifier = EmailClassifier()
        result = classifier.classify(content)
        print(f"分类结果: {result}")
    else:
        print("命令错误")


if __name__ == '__main__':
    main()
