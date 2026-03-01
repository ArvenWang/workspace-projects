#!/usr/bin/env python3
"""
GenericAgent 工具封装
将复旦大学的 9 个核心工具封装为可调用模块
"""

import json
import os
import sys
import tempfile
import subprocess
import threading
import time
from pathlib import Path

# ========== 工具 1: code_run ==========
def code_run(code, code_type="python", timeout=60, cwd=None):
    """执行 Python/Bash 代码"""
    preview = (code[:60].replace('\n', ' ') + '...') if len(code) > 60 else code.strip()
    print(f"[code_run] Running {code_type}: {preview}")
    
    cwd = cwd or os.path.join(os.getcwd(), 'temp')
    os.makedirs(cwd, exist_ok=True)
    tmp_path = None
    
    if code_type == "python":
        tmp_file = tempfile.NamedTemporaryFile(suffix=".ai.py", delete=False, mode='w', encoding='utf-8')
        tmp_file.write(code)
        tmp_path = tmp_file.name
        tmp_file.close()
        cmd = [sys.executable, "-X", "utf8", "-u", tmp_path]
    elif code_type in ["bash", "powershell"]:
        if os.name == 'nt':
            cmd = ["powershell", "-NoProfile", "-NonInteractive", "-Command", code]
        else:
            cmd = ["bash", "-c", code]
    else:
        return {"status": "error", "msg": f"不支持的类型: {code_type}"}
    
    full_stdout = []
    
    def stream_reader(proc, logs):
        for line_bytes in iter(proc.stdout.readline, b''):
            try:
                line = line_bytes.decode('utf-8')
            except UnicodeDecodeError:
                line = line_bytes.decode('gbk', errors='ignore')
            logs.append(line)
            print(line, end="")
    
    try:
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            bufsize=0, cwd=cwd
        )
        start_t = time.time()
        t = threading.Thread(target=stream_reader, args=(process, full_stdout), daemon=True)
        t.start()
        
        while t.is_alive():
            if time.time() - start_t > timeout:
                process.kill()
                full_stdout.append("\n[Timeout Error] 超时强制终止")
                break
            time.sleep(0.5)
        
        t.join(timeout=1)
        exit_code = process.poll()
        
        stdout_str = "".join(full_stdout)
        status = "success" if exit_code == 0 else "error"
        
        return {
            "status": status,
            "stdout": stdout_str[:8000],
            "exit_code": exit_code
        }
    except Exception as e:
        return {"status": "error", "msg": str(e)}
    finally:
        if code_type == "python" and tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


# ========== 工具 2: file_read ==========
def file_read(path, start=1, count=200, keyword=None, show_linenos=True):
    """读取文件内容"""
    try:
        if not os.path.exists(path):
            return {"status": "error", "msg": f"文件不存在: {path}"}
        
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        
        if keyword:
            # 搜索关键字
            for i, line in enumerate(lines, 1):
                if keyword.lower() in line.lower():
                    start = max(1, i - 5)
                    count = 20
                    break
        
        end = min(start + count - 1, total_lines)
        content_lines = lines[start-1:end]
        
        result = {
            "status": "success",
            "total_lines": total_lines,
            "lines": content_lines,
            "line_count": len(content_lines)
        }
        
        if show_linenos:
            result["content"] = ''.join([f"{i:4d} | {line}" for i, line in enumerate(content_lines, start)])
        else:
            result["content"] = ''.join(content_lines)
        
        return result
    
    except Exception as e:
        return {"status": "error", "msg": str(e)}


# ========== 工具 3: file_patch ==========
def file_patch(path, old_content, new_content):
    """精细化局部文件修改"""
    try:
        if not os.path.exists(path):
            return {"status": "error", "msg": f"文件不存在: {path}"}
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查 old_content 是否唯一
        count = content.count(old_content)
        if count == 0:
            return {"status": "error", "msg": "未找到要替换的内容"}
        if count > 1:
            return {"status": "error", "msg": f"找到 {count} 处匹配，请确保 old_content 唯一"}
        
        new_content_final = content.replace(old_content, new_content, 1)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content_final)
        
        return {"status": "success", "msg": f"已修改: {path}"}
    
    except Exception as e:
        return {"status": "error", "msg": str(e)}


# ========== 工具 4: file_write ==========
def file_write(path, content, mode="overwrite"):
    """文件写入"""
    try:
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
        
        if mode == "overwrite":
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
        elif mode == "append":
            with open(path, 'a', encoding='utf-8') as f:
                f.write(content)
        elif mode == "prepend":
            with open(path, 'r', encoding='utf-8') as f:
                existing = f.read()
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content + existing)
        else:
            return {"status": "error", "msg": f"不支持的模式: {mode}"}
        
        return {"status": "success", "msg": f"已写入: {path}"}
    
    except Exception as e:
        return {"status": "error", "msg": str(e)}


# ========== 工具 5: web_scan ==========
def web_scan(tabs_only=False):
    """获取页面内容 - 需要 browser_bridge"""
    # 导入 browser_bridge
    try:
        from browser_bridge import BrowserBridge
        import asyncio
        
        async def scan():
            bridge = BrowserBridge()
            # 等待连接
            await asyncio.sleep(1)
            if bridge.default_session:
                return await bridge.scan_page()
            else:
                return {"status": "error", "msg": "没有活跃的浏览器会话"}
        
        result = asyncio.run(scan())
        return result
    
    except ImportError:
        return {"status": "error", "msg": "browser_bridge 未安装"}
    except Exception as e:
        return {"status": "error", "msg": str(e)}


# ========== 工具 6: web_execute_js ==========
def web_execute_js(script, save_to_file=None):
    """执行 JavaScript"""
    try:
        from browser_bridge import BrowserBridge
        import asyncio
        
        async def run_js():
            bridge = BrowserBridge()
            await asyncio.sleep(0.5)
            if bridge.default_session:
                result = await bridge.execute_js(script)
                if save_to_file:
                    with open(save_to_file, 'w', encoding='utf-8') as f:
                        f.write(str(result))
                return {"status": "success", "result": result}
            else:
                return {"status": "error", "msg": "没有活跃的浏览器会话"}
        
        result = asyncio.run(run_js())
        return result
    
    except ImportError:
        return {"status": "error", "msg": "browser_bridge 未安装"}
    except Exception as e:
        return {"status": "error", "msg": str(e)}


# ========== 工具 7: ask_user ==========
def ask_user(question, candidates=None):
    """向用户提问 - 返回特殊状态让 Agent 暂停"""
    return {
        "status": "INTERRUPT",
        "intent": "HUMAN_INTERVENTION",
        "data": {
            "question": question,
            "candidates": candidates or []
        }
    }


# ========== 工具 8: update_working_checkpoint ==========
class WorkingCheckpoint:
    """工作便签管理器"""
    _instance = None
    _data = {}
    
    @classmethod
    def update(cls, key_info, related_sop=None):
        cls._data['key_info'] = key_info
        cls._data['related_sop'] = related_sop or []
        cls._data['updated_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
        return {"status": "success", "msg": "工作便签已更新"}
    
    @classmethod
    def get(cls):
        return cls._data.get('key_info', '')
    
    @classmethod
    def clear(cls):
        cls._data = {}
        return {"status": "success", "msg": "工作便签已清除"}


# ========== 工具 9: start_long_term_update ==========
def start_long_term_update():
    """准备长期记忆更新"""
    return {
        "status": "INTERRUPT",
        "intent": "LONG_TERM_MEMORY_UPDATE",
        "data": {"message": "请总结需要长期记忆的信息"}
    }


# ========== 工具注册表 ==========
TOOLS_REGISTRY = {
    "code_run": {
        "func": code_run,
        "description": "执行 Python/Bash 代码"
    },
    "file_read": {
        "func": file_read,
        "description": "读取文件内容"
    },
    "file_patch": {
        "func": file_patch,
        "description": "精细化局部文件修改"
    },
    "file_write": {
        "func": file_write,
        "description": "新建/覆盖/追加文件"
    },
    "web_scan": {
        "func": web_scan,
        "description": "获取页面内容"
    },
    "web_execute_js": {
        "func": web_execute_js,
        "description": "执行 JavaScript 控制浏览器"
    },
    "ask_user": {
        "func": ask_user,
        "description": "向用户提问"
    },
    "update_working_checkpoint": {
        "func": WorkingCheckpoint.update,
        "description": "更新工作便签"
    },
    "start_long_term_update": {
        "func": start_long_term_update,
        "description": "准备长期记忆更新"
    }
}


def execute_tool(tool_name, **kwargs):
    """执行工具的统一入口"""
    if tool_name not in TOOLS_REGISTRY:
        return {"status": "error", "msg": f"未知工具: {tool_name}"}
    
    func = TOOLS_REGISTRY[tool_name]["func"]
    try:
        return func(**kwargs)
    except Exception as e:
        return {"status": "error", "msg": str(e)}


if __name__ == '__main__':
    # 测试
    print("=== 测试 code_run ===")
    print(code_run("print('Hello from GenericAgent!')"))
    
    print("\n=== 测试 file_read ===")
    print(file_read("ga.py", count=5))
