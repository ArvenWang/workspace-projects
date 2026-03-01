#!/usr/bin/env python3
"""
DiversityController - 多样性控制
"""

import logging

logger = logging.getLogger("xhs_agent.diversity")


class DiversityController:
    """多样性控制器"""
    
    PATTERNS = {
        "question": {"markers": ["？", "?", "怎么", "为什么", "难道", "是不是"]},
        "analogy": {"markers": ["就像", "好比", "如同", "仿佛", "相当于"]},
        "supplement": {"markers": ["另外", "还有", "想到一个", "说到这个", "补充"]},
        "reverse": {"markers": ["不过", "但是", "然而", "本来以为", "没想到", "结果"]},
        "story": {"markers": ["上次", "有一次", "之前", "记得"]},
        "exclaim": {"markers": ["哈哈", "笑死", "绷不住", "离谱", "！"]},
        "fieldnote": {"markers": ["田野笔记", "观察记录", "人类行为"]},
    }
    
    def __init__(self):
        self.recent_patterns = []
    
    def detect_pattern(self, comment: str) -> str:
        """检测句式"""
        # 按marker长度降序匹配
        for name, info in sorted(self.PATTERNS.items(), 
                                  key=lambda x: -max(len(m) for m in x[1]["markers"])):
            if any(m in comment for m in info["markers"]):
                return name
        return "neutral"
    
    def check_and_fix(self, comment: str, rewrite_fn=None) -> str:
        """检查并修正多样性"""
        current = self.detect_pattern(comment)
        recent_5 = self.recent_patterns[-5:] if self.recent_patterns else []
        
        # 检查是否重复
        needs_rewrite = (
            (current in recent_5 and current != "neutral") or
            (len(self.recent_patterns) >= 10 and 
             self.recent_patterns[-10:].count(current) >= 3)
        )
        
        # 需要重写
        if needs_rewrite and rewrite_fn:
            excluded = set(recent_5)
            available = [p for p in self.PATTERNS if p not in excluded]
            if available:
                comment = rewrite_fn(comment, available[0])
                current = self.detect_pattern(comment)
        
        # 更新记录
        self.recent_patterns.append(current)
        self.recent_patterns = self.recent_patterns[-20:]
        
        return comment
