#!/usr/bin/env python3
"""
案例33: Git历史清理
功能：
1. 清除敏感信息
2. 重写历史

运行：
python3 git_cleaner.py check
python3 git_cleaner.py clean
"""

import os
import re


class GitCleaner:
    def __init__(self):
        self.secrets = [
            'api_key',
            'password',
            'secret',
            'token',
            'AKIA',  # AWS
        ]
    
    def check(self, repo_path='.'):
        """检查敏感信息"""
        print(f"\n🔍 检查Git历史...")
        
        # 检查.gitignore
        if os.path.exists('.gitignore'):
            print("  ✅ .gitignore存在")
        else:
            print("  ⚠️ 建议创建 .gitignore")
        
        # 检查敏感文件
        sensitive = ['.env', 'secrets.json', 'credentials.json']
        
        for f in sensitive:
            if os.path.exists(f):
                print(f"  ⚠️ 发现敏感文件: {f}")
        
        print("  ✅ 检查完成")
    
    def clean(self):
        """清理建议"""
        print("""
⚠️ 清理Git历史需要:

1. 删除敏感文件
   git rm --cached secrets.json

2. 重写历史 (危险!)
   git filter-branch --tree-filter 'rm -f secrets.json' HEAD
   
   或使用 BFG:
   bfg --delete-files secrets.json

3. 强制推送
   git push --force
""")


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""
Git历史清理 - 使用说明

使用:
  python3 git_cleaner.py check
  python3 git_cleaner.py clean

示例:
  python3 git_cleaner.py check
""")
        sys.exit(1)
    
    cmd = sys.argv[1]
    cleaner = GitCleaner()
    
    if cmd == 'check':
        cleaner.check()
    elif cmd == 'clean':
        cleaner.clean()
    else:
        print("命令错误")


if __name__ == '__main__':
    main()
