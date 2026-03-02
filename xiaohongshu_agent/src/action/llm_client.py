#!/usr/bin/env python3
"""
LLM 客户端 - MiniMax API
"""

import os
import json
import logging
import requests

logger = logging.getLogger("xhs_agent.llm")


class LLMClient:
    """LLM 客户端"""
    
    def __init__(self, config: dict):
        self.config = config
        self.api_key = config.get('api_key') or os.getenv('MINIMAX_API_KEY')
        self.base_url = config.get('base_url', 'https://api.minimax.chat/v1')
        self.model = config.get('model', 'MiniMax-M2.1')
    
    def generate(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
        """生成文本"""
        if not self.api_key:
            logger.warning("未配置 API Key")
            return ""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/text/chatcompletion_v2",
                headers=headers,
                json=data,
                timeout=30
            )
            
            result = response.json()
            
            if result.get('choices'):
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"LLM返回错误: {result}")
                return ""
                
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            return ""
    
    def rewrite(self, content: str, target_pattern: str = None) -> str:
        """重写内容（用于多样性控制）"""
        prompt = f"""请将以下评论改写成不同的句式风格：

原文：{content}
"""
        if target_pattern:
            prompt += f"\n目标风格：{target_pattern}"
        
        prompt += "\n直接输出改写后的内容，不要其他解释。"
        
        return self.generate(prompt, max_tokens=100)
    
    def count_tokens(self, text: str) -> int:
        """估算token数（简单估算：中文约1.5字符/token，英文约4字符/token）"""
        chinese = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        english = sum(1 for c in text if c.isascii())
        other = len(text) - chinese - english
        
        return int(chinese / 1.5 + english / 4 + other / 4)
