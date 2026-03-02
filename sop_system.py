#!/usr/bin/env python3
"""
SOP 自进化系统
任务完成后自动保存为 SOP，支持检索和执行
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path


class SOPSystem:
    """
    SOP (Standard Operating Procedure) 自进化系统
    
    功能:
    - 任务解决后自动保存为 SOP
    - 支持 SOP 检索
    - 支持 SOP 执行
    """
    
    def __init__(self, memory_dir="./memory"):
        self.memory_dir = memory_dir
        self.sops_dir = os.path.join(memory_dir, "sops")
        os.makedirs(self.sops_dir, exist_ok=True)
        
        # L1 索引文件
        self.index_file = os.path.join(memory_dir, "sop_index.json")
        self.index = self._load_index()
    
    def _load_index(self):
        """加载索引"""
        if os.path.exists(self.index_file):
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"sops": [], "last_updated": None}
    
    def _save_index(self):
        """保存索引"""
        self.index["last_updated"] = datetime.now().isoformat()
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)
    
    def create_sop(self, name, description, steps, tags=None):
        """
        创建新的 SOP
        
        Args:
            name: SOP 名称
            description: 描述
            steps: 步骤列表 [{"tool": "xxx", "args": {...}}, ...]
            tags: 标签列表
        """
        # 生成文件名
        safe_name = re.sub(r'[^\w\-_]', '_', name.lower())
        filename = f"{safe_name}_sop.md"
        filepath = os.path.join(self.sops_dir, filename)
        
        # 生成内容
        content = f"""# {name}

{description}

## 创建时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 标签
{', '.join(tags or [])}

## 步骤

"""
        for i, step in enumerate(steps, 1):
            tool = step.get('tool', 'unknown')
            args = step.get('args', {})
            note = step.get('note', '')
            
            content += f"### 步骤 {i}: {tool}\n"
            content += f"```json\n{json.dumps(args, ensure_ascii=False, indent=2)}\n```\n"
            if note:
                content += f"**注意**: {note}\n"
            content += "\n"
        
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 更新索引
        sop_entry = {
            "name": name,
            "filename": filename,
            "description": description,
            "tags": tags or [],
            "steps_count": len(steps),
            "created_at": datetime.now().isoformat()
        }
        self.index["sops"].append(sop_entry)
        self._save_index()
        
        return {"status": "success", "filepath": filepath, "sop": sop_entry}
    
    def record_task(self, task_name, tool_calls, result):
        """
        记录任务执行过程（用于后续创建 SOP）
        
        Args:
            task_name: 任务名称
            tool_calls: 工具调用列表 [{"tool": "xxx", "args": {...}}, ...]
            result: 执行结果
        """
        # 保存到临时记录
        record_file = os.path.join(self.memory_dir, "task_records.json")
        records = []
        
        if os.path.exists(record_file):
            with open(record_file, 'r', encoding='utf-8') as f:
                records = json.load(f)
        
        record = {
            "task_name": task_name,
            "tool_calls": tool_calls,
            "result": str(result)[:500],
            "recorded_at": datetime.now().isoformat()
        }
        records.append(record)
        
        with open(record_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        
        return {"status": "success", "records_count": len(records)}
    
    def suggest_sop_creation(self, task_name, tool_calls):
        """
        根据工具调用建议是否创建 SOP
        
        如果一个任务调用了 3+ 个工具，建议创建 SOP
        """
        if len(tool_calls) >= 3:
            return {
                "suggestion": "CREATE_SOP",
                "reason": f"此任务调用了 {len(tool_calls)} 个工具，值得保存为 SOP",
                "task_name": task_name,
                "steps": tool_calls
            }
        return {"suggestion": "SKIP", "reason": "任务较简单，无需创建 SOP"}
    
    def search_sops(self, query, tags=None):
        """
        搜索 SOP
        
        Args:
            query: 搜索关键词
            tags: 标签过滤
        """
        results = []
        
        for sop in self.index.get("sops", []):
            # 标签过滤
            if tags:
                if not any(tag in sop.get("tags", []) for tag in tags):
                    continue
            
            # 关键词搜索
            if query:
                q = query.lower()
                if q not in sop.get("name", "").lower() and q not in sop.get("description", "").lower():
                    continue
            
            results.append(sop)
        
        return results
    
    def get_sop(self, name_or_filename):
        """获取 SOP 内容"""
        # 查找文件
        if not name_or_filename.endswith(".md"):
            name_or_filename = name_or_filename + "_sop.md"
        
        filepath = os.path.join(self.sops_dir, name_or_filename)
        
        if not os.path.exists(filepath):
            # 尝试搜索
            for sop in self.index.get("sops", []):
                if name_or_filename in sop.get("filename", ""):
                    filepath = os.path.join(self.sops_dir, sop["filename"])
                    break
        
        if not os.path.exists(filepath):
            return {"status": "error", "msg": f"SOP 不存在: {name_or_filename}"}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {"status": "success", "content": content}
    
    def list_sops(self):
        """列出所有 SOP"""
        return {
            "sops": self.index.get("sops", []),
            "total": len(self.index.get("sops", []))
        }
    
    def delete_sop(self, name):
        """删除 SOP"""
        # 找到文件
        filename = None
        for sop in self.index["sops"]:
            if sop["name"] == name or sop["filename"] == name:
                filename = sop["filename"]
                break
        
        if not filename:
            return {"status": "error", "msg": f"SOP 不存在: {name}"}
        
        filepath = os.path.join(self.sops_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        
        # 从索引中移除
        self.index["sops"] = [s for s in self.index["sops"] if s["filename"] != filename]
        self._save_index()
        
        return {"status": "success", "msg": f"已删除: {filename}"}


# ========== 与 Agent 集成 ==========
class SOPSaver:
    """SOP 保存器 - 集成到 Agent 循环"""
    
    def __init__(self, sop_system: SOPSystem):
        self.sop_system = sop_system
        self.current_task = None
        self.tool_calls = []
    
    def start_task(self, task_name: str):
        """开始新任务"""
        self.current_task = task_name
        self.tool_calls = []
        print(f"[SOP] 开始任务: {task_name}")
    
    def record_tool_call(self, tool_name: str, args: dict):
        """记录工具调用"""
        self.tool_calls.append({
            "tool": tool_name,
            "args": args
        })
    
    def finish_task(self, result):
        """完成任务，检查是否需要创建 SOP"""
        if not self.current_task:
            return
        
        # 检查是否建议创建 SOP
        suggestion = self.sop_system.suggest_sop_creation(
            self.current_task, 
            self.tool_calls
        )
        
        if suggestion["suggestion"] == "CREATE_SOP":
            print(f"[SOP] 建议创建 SOP: {self.current_task}")
            print(f"       工具调用数: {len(self.tool_calls)}")
            return suggestion
        
        self.current_task = None
        self.tool_calls = []
        return None
    
    def auto_create_sop(self, name, description, tags=None):
        """自动从记录创建 SOP"""
        if not self.tool_calls:
            return {"status": "error", "msg": "没有工具调用记录"}
        
        return self.sop_system.create_sop(
            name=name,
            description=description,
            steps=self.tool_calls,
            tags=tags
        )


# ========== 测试 ==========
if __name__ == '__main__':
    print("=== 测试 SOP 系统 ===")
    
    # 创建 SOP 系统
    sop_system = SOPSystem(memory_dir="./memory")
    
    # 创建 SOP
    result = sop_system.create_sop(
        name="读取文件内容",
        description="通用文件读取 SOP",
        steps=[
            {"tool": "file_read", "args": {"path": "${path}", "count": 100}},
        ],
        tags=["文件", "读取", "通用"]
    )
    print(f"创建 SOP: {result}")
    
    # 搜索
    results = sop_system.search_sops("文件")
    print(f"搜索结果: {results}")
    
    # 列出
    print(f"所有 SOP: {sop_system.list_sops()}")
