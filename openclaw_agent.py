#!/usr/bin/env python3
"""
OpenClaw GenericAgent 整合模块
=====================
将复旦大学 GenericAgent 与 OpenClaw 融合

功能:
- 9 个核心工具 (ga_tools)
- Agent 循环执行器 (generic_agent_loop)
- SOP 自进化系统 (sop_system)
- 浏览器桥接 (browser_bridge)

使用:
    from openclaw_agent import OpenClawAgent
    
    agent = OpenClawAgent()
    result = agent.run("帮我查一下天气")
"""

import os
import sys

# 导入子模块
from generic_agent_tools import TOOLS_REGISTRY, execute_tool, WorkingCheckpoint
from generic_agent_loop import GenericAgentLoop
from sop_system import SOPSystem, SOPSaver


# ========== 工具 Schema (用于 LLM) ==========
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "code_run",
            "description": "代码执行器。优先使用python，仅在必要系统操作时使用 bash/powershell。",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "要执行的代码"},
                    "code_type": {"type": "string", "enum": ["python", "bash", "powershell"], "default": "python"},
                    "timeout": {"type": "integer", "default": 60}
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "file_read",
            "description": "读取文件内容。支持分页读取或关键字搜索。",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "start": {"type": "integer", "default": 1},
                    "count": {"type": "integer", "default": 200},
                    "keyword": {"type": "string"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "file_patch",
            "description": "精细化局部文件修改。",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "old_content": {"type": "string"},
                    "new_content": {"type": "string"}
                },
                "required": ["path", "old_content", "new_content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "file_write",
            "description": "文件新建、覆盖或追加。",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                    "mode": {"type": "string", "enum": ["overwrite", "append", "prepend"]}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_scan",
            "description": "获取当前页面的简化HTML内容。",
            "parameters": {
                "type": "object",
                "properties": {
                    "tabs_only": {"type": "boolean", "default": False}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_execute_js",
            "description": "万能网页操控。通过执行 JavaScript 控制浏览器。",
            "parameters": {
                "type": "object",
                "properties": {
                    "script": {"type": "string"},
                    "save_to_file": {"type": "string"}
                },
                "required": ["script"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ask_user",
            "description": "当需要用户决策时，调用此工具提问。",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "candidates": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["question"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_working_checkpoint",
            "description": "短期工作便签，防长任务信息丢失。",
            "parameters": {
                "type": "object",
                "properties": {
                    "key_info": {"type": "string"},
                    "related_sop": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["key_info"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "start_long_term_update",
            "description": "准备提炼长期记忆。",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]


# ========== 主类 ==========
class OpenClawAgent:
    """
    OpenClaw GenericAgent 主类
    
    用法:
        agent = OpenClawAgent()
        
        # 简单任务
        result = agent.run("今天天气怎么样")
        
        # 带 LLM 客户端
        result = agent.run("帮我写一个函数", llm_client=my_llm)
    """
    
    def __init__(self, memory_dir="./memory", max_turns=40, verbose=True):
        self.max_turns = max_turns
        self.verbose = verbose
        
        # 初始化组件
        self.sop_system = SOPSystem(memory_dir=memory_dir)
        self.sop_saver = SOPSaver(self.sop_system)
        self.agent_loop = GenericAgentLoop(max_turns=max_turns, verbose=verbose)
        self.agent_loop.set_tools_schema(TOOLS_SCHEMA)
        
        # 加载系统提示词
        self._load_system_prompt()
    
    def _load_system_prompt(self):
        """加载系统提示词"""
        prompt_file = os.path.join(os.path.dirname(__file__), "assets", "sys_prompt.txt")
        if os.path.exists(prompt_file):
            with open(prompt_file, 'r', encoding='utf-8') as f:
                self.agent_loop.set_system_prompt(f.read())
    
    def run(self, task: str, llm_client=None) -> dict:
        """
        执行任务
        
        Args:
            task: 任务描述
            llm_client: LLM 客户端（需实现 chat 方法）
            
        Returns:
            执行结果
        """
        # 记录开始
        self.sop_saver.start_task(task)
        
        # 运行 Agent
        result = self.agent_loop.run(task, llm_client)
        
        # 任务完成检查
        finish_suggestion = self.sop_saver.finish_task(result)
        
        if finish_suggestion and finish_suggestion.get("suggestion") == "CREATE_SOP":
            result["sop_suggestion"] = finish_suggestion
        
        return result
    
    def run_with_llm(self, task: str, api_key: str, model: str = "claude-3-5-sonnet-20241022") -> dict:
        """
        使用内置 LLM 执行任务
        
        Args:
            task: 任务描述
            api_key: API 密钥
            model: 模型名称
        """
        # 创建简单 LLM 客户端
        from openclaw_agent import AnthropicClient
        client = AnthropicClient(api_key=api_key, model=model)
        return self.run(task, llm_client=client)
    
    def create_sop(self, name: str, description: str, steps: list, tags: list = None) -> dict:
        """手动创建 SOP"""
        return self.sop_system.create_sop(name, description, steps, tags)
    
    def search_sops(self, query: str = "", tags: list = None) -> list:
        """搜索 SOP"""
        return self.sop_system.search_sops(query, tags)
    
    def list_sops(self) -> dict:
        """列出所有 SOP"""
        return self.sop_system.list_sops()


# ========== 简单 LLM 客户端 ==========
class AnthropicClient:
    """Anthropic Claude 客户端"""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.anthropic.com/v1/messages"
    
    def chat(self, messages: list, tools: list = None) -> dict:
        """发送聊天请求"""
        import requests
        
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        # 转换消息格式
        converted_messages = []
        for msg in messages:
            if msg["role"] == "system":
                continue  # system prompt 单独处理
            converted_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        payload = {
            "model": self.model,
            "messages": converted_messages,
            "max_tokens": 4096
        }
        
        if tools:
            payload["tools"] = tools
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            
            # 转换为标准格式
            content = result["content"][0]["text"]
            
            # 检查是否有工具调用
            if result.get("content") and len(result["content"]) > 1:
                # 有工具调用
                tool_use = result["content"][1]
                return {
                    "content": content,
                    "tool_calls": [
                        {
                            "function": {
                                "name": tool_use["name"],
                                "arguments": json.dumps(tool_use["input"])
                            }
                        }
                    ]
                }
            else:
                return {"content": content, "tool_calls": []}
                
        except Exception as e:
            return {"error": str(e)}


import json


# ========== CLI 入口 ==========
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenClaw GenericAgent")
    parser.add_argument("task", nargs="?", help="任务描述")
    parser.add_argument("--api-key", help="Anthropic API Key")
    parser.add_argument("--model", default="claude-3-5-sonnet-20241022", help="模型")
    parser.add_argument("--sops", action="store_true", help="列出所有 SOP")
    parser.add_argument("--search", help="搜索 SOP")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    agent = OpenClawAgent(verbose=args.verbose)
    
    # 列出 SOP
    if args.sops:
        print(json.dumps(agent.list_sops(), ensure_ascii=False, indent=2))
        return
    
    # 搜索 SOP
    if args.search:
        results = agent.search_sops(args.search)
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return
    
    # 执行任务
    if args.task:
        if not args.api_key:
            print("错误: 需要 --api-key")
            return
        
        print(f"🤔 任务: {args.task}")
        result = agent.run_with_llm(args.task, args.api_key, args.model)
        print(f"\n📊 结果: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
