#!/usr/bin/env python3
"""
案例56: Email Auto-Sorter
"""

class EmailAutoSorter:
    def __init__(self):
        self.rules = [
            ('紧急', ['urgent', 'asap', '紧急']),
            ('工作', ['meeting', 'project', '会议']),
            ('个人', ['personal', '私人']),
        ]
    
    def sort(self, subject):
        for category, keywords in self.rules:
            for kw in keywords:
                if kw.lower() in subject.lower():
                    return category
        return '其他'


if __name__ == '__main__':
    sorter = EmailAutoSorter()
    print(sorter.sort("紧急会议通知"))
    print(sorter.sort("项目更新"))
