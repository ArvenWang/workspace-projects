#!/usr/bin/env python3
"""
文件整理AI助手
能帮你做什么：
1. 自动分类文件
2. 按类型整理
3. 按日期整理
4. 清理重复文件
5. 智能重命名

使用方式：
python3 file_organizer.py organize ~/Downloads
python3 file_organizer.py clean ~/Documents
python3 file_organizer.py rename ~/Desktop
"""

import os
import shutil
import json
import hashlib
from datetime import datetime
from collections import defaultdict

# 配置
CONFIG = {
    'rules': {
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'],
        'videos': ['.mp4', '.avi', '.mov', '.mkv', '.flv'],
        'documents': ['.pdf', '.doc', '.docx', '.txt', '.md', '.xls', '.xlsx', '.ppt', '.pptx'],
        'archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
        'code': ['.py', '.js', '.java', '.cpp', '.c', '.go', '.rs', '.html', '.css'],
        'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg'],
    }
}

def get_file_hash(filepath):
    """计算文件hash"""
    md5 = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                md5.update(chunk)
        return md5.hexdigest()
    except:
        return None

def scan_directory(directory):
    """扫描目录"""
    files = []
    
    for root, dirs, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(root, filename)
            ext = os.path.splitext(filename)[1].lower()
            
            files.append({
                'name': filename,
                'path': filepath,
                'ext': ext,
                'size': os.path.getsize(filepath),
                'modified': datetime.fromtimestamp(os.path.getmtime(filepath)),
            })
    
    return files

def categorize_file(ext):
    """分类文件"""
    for category, extensions in CONFIG['rules'].items():
        if ext in extensions:
            return category
    return 'others'

def organize_by_type(directory):
    """按类型整理"""
    files = scan_directory(directory)
    stats = defaultdict(int)
    
    for f in files:
        category = categorize_file(f['ext'])
        
        # 创建分类目录
        target_dir = os.path.join(directory, category)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        
        # 移动文件
        target_path = os.path.join(target_dir, f['name'])
        
        if f['path'] != target_path:
            try:
                shutil.move(f['path'], target_path)
                stats[category] += 1
            except Exception as e:
                print(f"❌ 移动失败: {f['name']} - {e}")
    
    print("✅ 整理完成!")
    for cat, count in stats.items():
        print(f"  {cat}: {count}个文件")

def find_duplicates(directory):
    """查找重复文件"""
    files = scan_directory(directory)
    hashes = defaultdict(list)
    
    print("🔍 扫描重复文件...")
    
    for f in files:
        if f['size'] > 1000:  # 忽略小文件
            file_hash = get_file_hash(f['path'])
            if file_hash:
                hashes[file_hash].append(f)
    
    # 找出重复
    duplicates = {k: v for k, v in hashes.items() if len(v) > 1}
    
    if duplicates:
        print(f"\n⚠️ 发现 {len(duplicates)} 组重复文件:")
        for hash, files in duplicates.items():
            print(f"\n  相同文件 ({len(files)}个):")
            for f in files:
                print(f"    - {f['path']}")
    else:
        print("✅ 没有发现重复文件")
    
    return duplicates

def clean_duplicates(directory):
    """清理重复文件"""
    duplicates = find_duplicates(directory)
    
    for hash, files in duplicates.items():
        # 保留第一个，删除其余
        for f in files[1:]:
            try:
                os.remove(f['path'])
                print(f"🗑️ 已删除: {f['path']}")
            except Exception as e:
                print(f"❌ 删除失败: {f['path']}")

def organize_by_date(directory):
    """按日期整理"""
    files = scan_directory(directory)
    stats = defaultdict(int)
    
    for f in files:
        # 按修改日期分类
        date_str = f['modified'].strftime('%Y-%m')
        target_dir = os.path.join(directory, date_str)
        
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        
        target_path = os.path.join(target_dir, f['name'])
        
        if f['path'] != target_path:
            try:
                shutil.move(f['path'], target_path)
                stats[date_str] += 1
            except:
                pass
    
    print("✅ 按日期整理完成!")
    for date, count in sorted(stats.items()):
        print(f"  {date}: {count}个文件")

def smart_rename(directory):
    """智能重命名"""
    files = scan_directory(directory)
    
    for f in files:
        old_name = f['name']
        name, ext = os.path.splitext(old_name)
        
        # 移除特殊字符
        new_name = ''.join(c if c.isalnum() or c in ' -_' else '_' for c in name)
        new_name = new_name.strip() + ext
        
        if new_name != old_name:
            new_path = os.path.join(os.path.dirname(f['path']), new_name)
            try:
                os.rename(f['path'], new_path)
                print(f"📝 {old_name} -> {new_name}")
            except:
                pass

# CLI
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 3:
        print("用法:")
        print("  python3 file_organizer.py organize <目录>  # 按类型整理")
        print("  python3 file_organizer.py bydate <目录>   # 按日期整理")
        print("  python3 file_organizer.py duplicate <目录>  # 查找重复")
        print("  python3 file_organizer.py clean <目录>    # 清理重复")
        print("  python3 file_organizer.py rename <目录>   # 智能重命名")
        sys.exit(1)
    
    cmd = sys.argv[1]
    directory = sys.argv[2]
    
    if cmd == 'organize':
        organize_by_type(directory)
    elif cmd == 'bydate':
        organize_by_date(directory)
    elif cmd == 'duplicate':
        find_duplicates(directory)
    elif cmd == 'clean':
        clean_duplicates(directory)
    elif cmd == 'rename':
        smart_rename(directory)
    else:
        print("未知命令")
