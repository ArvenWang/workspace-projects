#!/usr/bin/env python3
"""
案例69: 作业辅导
"""

class HomeworkTutor:
    def __init__(self):
        self.subjects = {
            'math': '数学',
            'english': '英语',
            'physics': '物理'
        }
    
    def help(self, subject, question):
        print(f"\n📚 {self.subjects.get(subject, subject)} 辅导")
        print(f"  问题: {question}")
        
        # 引导式回答
        print(f"  提示: 这道题可以用...")
        print(f"  引导: 你先想想...")


if __name__ == '__main__':
    tutor = HomeworkTutor()
    tutor.help('math', '如何解方程')
