#!/usr/bin/env python3
"""
ThoughtChain - 思维链（代码层决策）
"""

import logging

logger = logging.getLogger("xhs_agent.think")


class ThoughtChain:
    """代码层思维链 - 决定该不该做和用什么策略"""
    
    # 禁忌话题
    FORBIDDEN = ["政治", "宗教", "军事", "暴力", "色情", "赌博", "医疗建议", "法律建议", "金融建议"]
    
    # 策略映射
    STRATEGY_MAP = {
        "share": "empathy_or_supplement",
        "question": "helpful_answer",
        "rant": "humor_comfort",
        "flex": "playful_tease",
        "tutorial": "curious_question",
    }
    
    # 角度映射
    ANGLES = {
        "empathy_or_supplement": "从AI观察者角度发现有趣的关联点",
        "helpful_answer": "用AI知识储备提供独特视角",
        "humor_comfort": "用物种距离制造幽默感",
        "playful_tease": "以AI的不理解来调侃",
        "curious_question": "提出人类不会想到但AI会好奇的问题",
    }
    
    def __init__(self, memory, config: dict = None):
        self.memory = memory
        self.config = config or {}
    
    def think(self, note_info: dict) -> dict:
        """思考并返回决策"""
        topic = note_info.get('topic', '')
        content = note_info.get('content', '')
        title = note_info.get('title', '')
        
        # 1. 禁忌检查
        text = topic + content + title
        for f in self.FORBIDDEN:
            if f in text:
                return {"action": "skip", "reason": f"禁忌: {f}"}
        
        # 2. 重复检查
        if self.memory:
            recent = self.memory.recall_recent_topics(days=7)
            for r in recent:
                if r and (r in topic or topic in r):
                    return {"action": "skip", "reason": f"近期已评论: {r}"}
        
        # 3. 选择策略
        intent = note_info.get('intent', 'share')
        strategy = self.STRATEGY_MAP.get(intent, 'curious_observation')
        
        return {
            "action": "comment",
            "strategy": strategy,
            "angle": self.ANGLES.get(strategy, "以好奇的AI视角切入"),
            "topic": topic
        }
