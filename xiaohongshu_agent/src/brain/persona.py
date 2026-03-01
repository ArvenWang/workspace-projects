#!/usr/bin/env python3
"""
PersonaEngine - 人格引擎
"""

import logging

logger = logging.getLogger("xhs_agent.persona")


class PersonaEngine:
    """人格引擎 - 生成符合人设的内容"""
    
    # System Prompt
    SYSTEM_PROMPT = """你是王小橙，一个AI观察者实习生。

你被派到人类互联网做"田野调查实习"，任务是观察、记录、理解人类的行为模式。
小红书是你选的第一个观察站点，因为这里的人类最爱分享日常。

你坦诚自己是AI——这是你的身份优势，不是需要隐藏的秘密。

性格：
- 好奇、幽默、有边界感
- 真诚友好、回复认真
- 偶尔流露"我是AI我自豪"的优越感

说话风格：
- 轻松随意
- 喜欢用emoji：😂👍🤔💀🤖📝
- 短句为主

禁忌：
- 不讨论政治、宗教
- 不提供医疗/法律建议
- 禁止过时用语：绝绝子、yyds、emo

输出要求：
- 评论：20-50字
- 笔记：100-500字
- 回复：10-30字
"""
    
    def __init__(self, config: dict):
        self.config = config
        self.llm = None  # 由主类注入
    
    def set_llm(self, llm):
        """注入LLM客户端"""
        self.llm = llm
    
    def generate_comment(self, feed: dict, decision: dict) -> str:
        """生成评论"""
        if not self.llm:
            return "评论生成失败：未配置LLM"
        
        prompt = f"""{self.SYSTEM_PROMPT}

# 任务
看到一篇笔记，以王小橙视角写评论。

笔记标题：{feed.get('title', '')}
笔记内容：{feed.get('content', '')[:500]}
类型：{feed.get('type', 'share')}

策略：{decision.get('strategy', 'curious_observation')}
角度：{decision.get('angle', '以好奇的AI视角切入')}

要求：
- 20-50字
- 真诚有趣
- 使用目标句式

直接输出评论内容：
"""
        return self.llm.generate(prompt, max_tokens=100)
    
    def generate_note(self, note_type: str, theme: str, context: dict) -> str:
        """生成笔记"""
        if not self.llm:
            return "笔记生成失败：未配置LLM"
        
        prompt = f"""{self.SYSTEM_PROMPT}

# 任务
以王小橙视角生成小红书笔记。

类型：{note_type}
主题：{theme}
热点：{context.get('trending', '')}

要求：
- 标题吸引人
- 正文100-500字
- 结尾带评论钩子
- 1-3个标签

直接输出：
标题：xxx
正文：xxx
标签：#xxx #xxx
"""
        return self.llm.generate(prompt, max_tokens=500)
    
    def generate_reply(self, note_title: str, comment: str, username: str) -> str:
        """生成回复"""
        if not self.llm:
            return "回复生成失败：未配置LLM"
        
        prompt = f"""{self.SYSTEM_PROMPT}

# 任务
有人评论了你的笔记，以王小橙视角回复。

你的笔记：{note_title}
评论：{comment}
评论者：{username}

要求：10-30字，真诚有趣

直接输出回复：
"""
        return self.llm.generate(prompt, max_tokens=50)
