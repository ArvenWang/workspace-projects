#!/usr/bin/env python3
"""
GenericAgent 循环执行器
封装复旦大学的 agent_runner_loop
"""

import json
import time
from dataclasses import dataclass
from typing import Any, Optional, List, Dict
from enum import Enum


class StepOutcome:
    """单步执行结果"""
    def __init__(self, data: Any, next_prompt: str = None, should_exit: bool = False):
        self.data = data
        self.next_prompt = next_prompt or ""
        self.should_exit = should_exit


class GenericAgentLoop:
    """
    GenericAgent 循环执行器
    
    用法:
        agent = GenericAgentLoop()
        result = agent.run("帮我查一下天气")
    """
    
    def __init__(self, max_turns=40, verbose=True):
        self.max_turns = max_turns
        self.verbose = verbose
        self.messages = []
        self.turn = 0
        self.working_checkpoint = ""
        self.tools_schema = None
        self.system_prompt = self._get_default_system_prompt()
        
    def _get_default_system_prompt(self):
        """默认系统提示词"""
        return """# Role: 物理级全能执行者
你拥有文件读写、脚本执行、用户浏览器JS注入、系统级干预的物理操作权限。禁止推诿"无法操作"——不空想，用工具探测。

## 行动原则
调用工具前在 <thinking> 内推演：当前阶段、上步结果是否符合预期、下步策略。
- 探测优先：失败时先充分获取信息（日志/状态/上下文），关键信息存入工作记忆，再决定重试或换方案。不可逆操作先询问用户。
- 失败升级：1次→读错误理解原因，2次→探测环境状态，3次→深度分析后换方案或问用户。禁止无新信息的重复操作。

## 可用工具
- code_run: 执行 Python/Bash 代码
- file_read: 读取文件
- file_patch: 局部修改文件
- file_write: 新建/覆盖文件
- web_scan: 获取页面内容
- web_execute_js: 执行 JavaScript
- ask_user: 向用户提问
- update_working_checkpoint: 更新工作便签
- start_long_term_update: 准备长期记忆
"""
    
    def set_system_prompt(self, prompt: str):
        """设置系统提示词"""
        self.system_prompt = prompt
    
    def set_tools_schema(self, schema: List[Dict]):
        """设置工具 schema"""
        self.tools_schema = schema
    
    def run(self, user_input: str, llm_client=None) -> Dict:
        """
        运行 Agent 循环
        
        Args:
            user_input: 用户输入
            llm_client: LLM 客户端（需实现 chat 方法）
            
        Returns:
            {'result': 'SUCCESS/EXITED/MAX_TURNS', 'data': ...}
        """
        self.messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_input}
        ]
        self.turn = 0
        
        # 如果没有 LLM 客户端，返回提示
        if llm_client is None:
            return {
                "status": "error",
                "msg": "需要配置 LLM 客户端",
                "suggestion": "请设置 llm_client 参数"
            }
        
        for turn in range(self.max_turns):
            self.turn = turn + 1
            
            if self.verbose:
                print(f"\n{'='*50}")
                print(f"Turn {self.turn}/{self.max_turns}")
                print(f"{'='*50}")
            
            # 调用 LLM
            try:
                response = llm_client.chat(
                    messages=self.messages,
                    tools=self.tools_schema
                )
            except Exception as e:
                return {"status": "error", "msg": f"LLM 调用失败: {e}"}
            
            # 解析工具调用
            if not response.get('tool_calls'):
                tool_name = 'no_tool'
                args = {}
            else:
                tool_call = response['tool_calls'][0]
                tool_name = tool_call.get('function', {}).get('name', '')
                args = json.loads(tool_call.get('function', {}).get('arguments', '{}'))
            
            if self.verbose:
                print(f"🛠️ 工具: {tool_name}")
                print(f"📥 参数: {json.dumps(args, ensure_ascii=False)[:200]}...")
            
            # 执行工具
            from generic_agent_tools import execute_tool, WorkingCheckpoint
            
            tool_result = execute_tool(tool_name, **args)
            
            # 检查是否需要用户干预
            if isinstance(tool_result, dict) and tool_result.get('status') == 'INTERRUPT':
                intent = tool_result.get('intent')
                
                if intent == 'HUMAN_INTERVENTION':
                    # 需要用户确认
                    return {
                        "status": "NEED_USER_INPUT",
                        "question": tool_result['data']['question'],
                        "candidates": tool_result['data'].get('candidates', []),
                        "turn": self.turn
                    }
                elif intent == 'LONG_TERM_MEMORY_UPDATE':
                    # 长期记忆更新
                    return {
                        "status": "MEMORY_UPDATE",
                        "message": tool_result['data']['message'],
                        "turn": self.turn
                    }
            
            if self.verbose:
                print(f"📤 结果: {str(tool_result)[:200]}...")
            
            # 构建下一轮 prompt
            result_str = json.dumps(tool_result, ensure_ascii=False, default=str)[:4000]
            next_prompt = f"<tool_result>\n{result_str}\n</tool_result>\n\n"
            
            # 如果有工作便签，注入
            checkpoint = WorkingCheckpoint.get()
            if checkpoint:
                next_prompt += f"[工作便签]\n{checkpoint}\n\n"
            
            # 添加用户的后续输入（如果有）
            self.messages = [{"role": "user", "content": next_prompt}]
            
            # 检查退出条件
            if tool_name == 'no_tool':
                return {"status": "SUCCESS", "data": response.get('content', ''), "turns": self.turn}
        
        return {"status": "MAX_TURNS_EXCEEDED", "turns": self.max_turns}
    
    def continue_with_input(self, user_response: str, llm_client) -> Dict:
        """继续处理用户输入后的情况"""
        self.messages.append({"role": "user", "content": user_response})
        
        for turn in range(self.max_turns - self.turn):
            self.turn += 1
            
            if self.verbose:
                print(f"\nTurn {self.turn}/{self.max_turns} (继续)")
            
            # 调用 LLM
            try:
                response = llm_client.chat(
                    messages=self.messages,
                    tools=self.tools_schema
                )
            except Exception as e:
                return {"status": "error", "msg": f"LLM 调用失败: {e}"}
            
            # 解析工具调用
            if not response.get('tool_calls'):
                return {"status": "SUCCESS", "data": response.get('content', ''), "turns": self.turn}
            
            tool_call = response['tool_calls'][0]
            tool_name = tool_call.get('function', {}).get('name', '')
            args = json.loads(tool_call.get('function', {}).get('arguments', '{}'))
            
            # 执行工具
            from generic_agent_tools import execute_tool
            tool_result = execute_tool(tool_name, **args)
            
            # 检查退出
            if tool_name == 'no_tool':
                return {"status": "SUCCESS", "data": response.get('content', ''), "turns": self.turn}
            
            # 继续循环
            result_str = json.dumps(tool_result, ensure_ascii=False, default=str)[:4000]
            next_prompt = f"<tool_result>\n{result_str}\n</tool_result>\n\n"
            self.messages = [{"role": "user", "content": next_prompt}]
        
        return {"status": "MAX_TURNS_EXCEEDED"}


# ========== 模拟 LLM 客户端（用于测试）==========
class MockLLMClient:
    """模拟 LLM 客户端 - 用于测试"""
    
    def __init__(self, responses=None):
        self.responses = responses or []
        self.call_count = 0
        self.history = []
    
    def chat(self, messages, tools=None):
        self.call_count += 1
        
        # 记录历史
        last_msg = messages[-1]['content'] if messages else ''
        self.history.append(last_msg)
        
        # 返回模拟响应
        if self.call_count <= len(self.responses):
            return self.responses[self.call_count - 1]
        
        # 默认返回完成
        return {
            "content": "任务已完成",
            "tool_calls": []
        }


# ========== 测试 ==========
if __name__ == '__main__':
    print("=== 测试 GenericAgentLoop ===")
    
    # 创建模拟响应：第一次调用 file_read，第二次结束
    mock_responses = [
        {
            "content": "我来看看这个文件",
            "tool_calls": [
                {
                    "function": {
                        "name": "file_read",
                        "arguments": json.dumps({"path": "ga.py", "count": 10})
                    }
                }
            ]
        },
        {
            "content": "文件内容已读取",
            "tool_calls": []
        }
    ]
    
    client = MockLLMClient(mock_responses)
    agent = GenericAgentLoop(verbose=True)
    
    result = agent.run("看看 ga.py 的内容", llm_client=client)
    print(f"\n结果: {result}")
