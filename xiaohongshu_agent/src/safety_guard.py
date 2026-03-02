#!/usr/bin/env python3
"""
SafetyGuard - 安全熔断组件
"""

import time
import logging
from collections import defaultdict
from typing import Dict, List

logger = logging.getLogger("xhs_agent.safety")


class SafetyGuard:
    """三层防护：规则层 → LLM层 → 熔断层"""
    
    # 稳定期频率阈值
    FREQUENCY_LIMIT = {
        "publish": {"max": 3, "unit": "day"},
        "comment": {"max": 8, "unit": "hour"},
        "like": {"max": 30, "unit": "hour"},
        "follow": {"max": 10, "unit": "hour"},
    }
    
    # 冷启动期（前30天）
    COLD_START_LIMIT = {
        "publish": {"max": 1, "unit": "day"},
        "comment": {"max": 3, "unit": "hour"},
        "like": {"max": 10, "unit": "hour"},
        "follow": {"max": 3, "unit": "hour"},
    }
    
    # 过时用语
    OUTDATED_WORDS = ["绝绝子", "yyds", "emo", "内卷", "躺平", "摆烂"]
    
    # 需要审核的词
    REVIEW_WORDS = ["赚钱", "副业", "变现", "引流", "私聊", "加我", "减肥", "药", "治疗"]
    
    def __init__(self, config: dict):
        self.config = config
        self.action_log = defaultdict(list)
        self.account_age_days = config.get('account_age_days', 0)
        self.block_words = self._load_wordlist(config.get('wordlist_path', 'config/sensitive_words.txt'))
        
    def _load_wordlist(self, path: str) -> List[str]:
        """加载敏感词库"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            logger.warning(f"词库不存在: {path}")
            return []
    
    def check(self, content: str, action_type: str) -> Dict:
        """检查内容"""
        # 1. 敏感词检查
        content_lower = content.lower()
        for word in self.block_words:
            if word.lower() in content_lower:
                return {"pass": False, "reason": f"敏感词: {word}", "level": "block"}
        
        # 2. 过时用语检查
        for word in self.OUTDATED_WORDS:
            if word in content:
                return {"pass": False, "reason": f"过时用语: {word}", "level": "rewrite"}
        
        # 3. 频率检查
        if not self._check_frequency(action_type):
            return {"pass": False, "reason": f"频率超限: {action_type}", "level": "wait"}
        
        # 4. 审核词检查
        review_found = [w for w in self.REVIEW_WORDS if w in content_lower]
        if review_found:
            return {"pass": True, "needs_review": True, "review_words": review_found}
        
        return {"pass": True, "needs_review": False}
    
    def _check_frequency(self, action_type: str) -> bool:
        """检查频率"""
        limits = self.COLD_START_LIMIT if self.account_age_days < 30 else self.FREQUENCY_LIMIT
        
        if action_type not in limits:
            return True
        
        limit = limits[action_type]
        cutoff = time.time() - (3600 if limit["unit"] == "hour" else 86400)
        
        # 清理过期记录
        self.action_log[action_type] = [t for t in self.action_log[action_type] if t > cutoff]
        
        return len(self.action_log[action_type]) < limit["max"]
    
    def record_action(self, action_type: str):
        """记录操作"""
        self.action_log[action_type].append(time.time())
    
    def review_high_risk(self, content: str, review_words: List[str]) -> Dict:
        """LLM二次审核"""
        # TODO: 实现独立LLM审核
        return {"safe": True, "reason": "审核通过"}
    
    def emergency_stop(self, reason: str):
        """紧急停止"""
        logger.critical(f"SafetyGuard 触发紧急停止: {reason}")
        # TODO: 通知主Agent
